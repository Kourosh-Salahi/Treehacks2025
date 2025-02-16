import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split
from sklearn.model_selection import train_test_split
from scipy.signal import find_peaks

class SquadMonitor():
  def __init__(self, squad_signals, squad_metadata, soldier_IDs, 
               signal_feature_names, metadata_feature_names, model, device, model_info, disease_classifier, label_encoder):
    self.squad_sigals = squad_signals
    self.squad_metadata = squad_metadata
    self.soldier_IDs = soldier_IDs
    self.signal_feature_names = signal_feature_names
    self.metadata_feature_names = metadata_feature_names
    # "model" is a trained model that generates metadata predictions from raw signals
    self.model = model.to(device)
    self.device = device

    # contains :
    # - maximum time steps that the model was trained on
    # - metadata mean per feature
    # - metadata std per feature
    self.model_info = model_info

    # trained logistic regression that predicts ["afib", "regular", "irregular"] from metadata
    self.disease_classifier = disease_classifier
    # fitted label encoder that maps from outcome to label encoding
    self.label_encoder = label_encoder

    self.explainer = lime_tabular.LimeTabularExplainer(
      training_data=squad_metadata,
      feature_names=self.metadata_feature_names,
      class_names=["afib", "irregular", "regular"],
      mode="classification"
    )

  # Generate_metadata for sequences (list of num_features, num_timesteps numpy arrays)
  def generate_metadata(self, sequences, soldier_IDs):
    padded_sequences = []
    masks = []
    for seq in sequences:
      seq_tensor = torch.tensor(seq, dtype=torch.float32)  # Convert numpy array to tensor
      pad_length = self.model_info["max_time"] - seq_tensor.shape[1]
      padded_seq = F.pad(seq_tensor, (0, pad_length), "constant", 0)
      mask = torch.zeros(self.model_info["max_time"], dtype=torch.bool)
      mask[seq_tensor.shape[1]:] = True  # Mask padded positions
      padded_sequences.append(padded_seq)
      masks.append(mask)
    padded_sequences = torch.tensor(padded_sequences, dtype=torch.float32).to(self.device)
    masks = torch.tensor(masks, dtype=torch.float32).to(self.device)
    outputs = model(padded_sequences, masks)
    outputs = outputs.cpu().detach().numpy()

    # un-normalize
    outputs = outputs * self.model_info["metadata_std"] + self.model_info["metadata_mean"]
    return pd.DataFrame(outputs, columns=self.metadata_feature_names, index=soldier_IDs)

  def visualize_one_metadata(self, one_soldier_metadata):
    # can do some percentile stuff on the front end
    pass

  def visualize_all_metadata(self, all_soldier_metadata):
    # can do some distribution stuff on the front end
    pass

  def generate_heart_metrics(self, sequences, soldier_IDs):
    # heart rate
    # mean RR interval
    # std of RR intervals
    # RMS of successive differences (SD)

    interval = 4e-3 # hard-coded 40 millisecond interval because ~1500 timesteps per minute

    green_idx = self.signal_feature_names.index("green")
    heart_rates = []
    mean_RRs = []
    std_RRs = []
    RMSSDs = []
    for seq, id in zip(sequences, soldier_IDs):
      peaks, _ = find_peaks(seq[green_idx], height=0)
      bpm = []
      for i in range(len(peaks)):
        bpm.append(1500 / peaks[i] * i)
      bpm = bpm[peaks[0]:]
      heart_rates.append(bpm)
      RR_intervals = np.diff(peaks) * interval
      mean_RRs.append(np.mean(RR_intervals))
      std_RRs.append(np.std(RR_intervals))
      RMSSDs.append(np.mean(np.diff(RR_intervals) ** 2) ** 0.5)
    return pd.DataFrame({"Heart Rate": heart_rates,
                         "Mean RR Interval": mean_RRs,
                         "SDNN": std_RRs,
                         "RMSSD": RMSSDs}, index=soldier_IDs)
  
  def generate_health_predictions(self, metadata, soldier_IDs):
    if len(metadata) == 1:
      metadata = metadata.reshape(1,-1)
    outputs = self.disease_classifier.predict(metadata)
    outputs = self.label_encoder.inverse_transform(outputs)
    return {soldier_IDs[i]: outputs[i] for i in range(len(soldier_IDs))}
  
  def optimize_cohort(self, cohort_metadata, cohort_IDs):
    all_outcomes = self.generate_health_predictions(self.squad_metadata, self.soldier_IDs)
    cohort_outcomes = self.generate_health_predictions(self.cohort_metadata, cohort_IDs)
    self.visualize_cohort(cohort_outcomes)
    
    num_regular = cohort_outcomes.values().count("regular")
    num_irregular = cohort_outcomes.values().count("irregular")
    num_afib = cohort_outcomes.values().count("afib")
    if num_irregular > 0 or num_afib > 0:
      self.alert_commander(num_irregular, num_afib)
      healthy_replacements = [ID for ID, condition in all_outcomes.items() if condition == "regular" and not ID in cohort_IDs]
      sampled_replacements = np.random.choice(healthy_replacements, size=num_irregular + num_afib, replace=False)
      to_replace = [ID for ID, condition in cohort_outcomes.items() if condition != "regular"]
      for i in to_replace:
        cohort_IDs.remove(i)
      for i in sampled_replacements:
        cohort_IDs.append(i)
      return cohort_IDs
    return cohort_IDs
  
  def visualize_cohort(self, cohort_outcomes):
    # can visualize cohort outcomes on the front end
    pass
  
  def alert_commander(self, num_irregular, num_afib):
    # can do some front end thing
    pass
  
  def explain_outcome(self, metadata_row):
    exp = self.explainer.explain_instance(
      data_row=metadata_row, 
      predict_fn=self.disease_classifier.predict_proba, num_features=len(self.metadata_feature_names))
    features = exp.as_map()
    exp.show_in_notebook()
    # figure out visualization on front end

  def end_to_end(self, signals, soldier_IDs):
    predicted_metadata = self.generate_metadata(signals, soldier_IDs)
    outcome_predictions = self.generate_health_predictions(predicted_metadata.values, soldier_IDs)
    return outcome_predictions
  