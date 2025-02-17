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
               signal_feature_names, metadata_feature_names, model, device, model_info, disease_classifier, label_encoder,
               lime_training_data):
    self.squad_signals = squad_signals
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
      training_data=lime_training_data,
      feature_names=self.metadata_feature_names,
      class_names=["afib", "irregular", "regular"],
      mode="classification"
    )

    self.activity_distribution = np.array(self.generate_background_activity())
    self.health_distribution = self.generate_background_health()

  def generate_background_activity(self):
    temp = []
    for signal in self.squad_signals:
      acc_x = signal[self.signal_feature_names.index("acc_x")]
      acc_y = signal[self.signal_feature_names.index("acc_y")]
      acc_z = signal[self.signal_feature_names.index("acc_z")]
      VM = (acc_x ** 2 + acc_y ** 2 + acc_z ** 2) ** 0.5
      temp.append(max(VM) - min(VM))
    return temp

  def generate_background_health(self):
    return self.disease_classifier.predict_proba(self.squad_metadata)[:,2]

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

    interval = 40e-3 # hard-coded 40 millisecond interval because ~1500 timesteps per minute

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
    probs = self.disease_classifier.predict_proba(metadata)[:,2]
    outputs = self.label_encoder.inverse_transform(outputs)
    percentiles = []
    for prob in probs:
      percentiles.append(np.sum(prob >= self.health_distribution) / self.health_distribution.shape[0])
    return {soldier_IDs[i]: (outputs[i], percentiles[i]) for i in range(len(soldier_IDs))}

  def generate_movement_data(self, signals, soldier_IDs):
    VM_range_percentiles = []
    for signal in signals:
      acc_x = signal[self.signal_feature_names.index("acc_x")]
      acc_y = signal[self.signal_feature_names.index("acc_y")]
      acc_z = signal[self.signal_feature_names.index("acc_z")]
      VM = (acc_x ** 2 + acc_y ** 2 + acc_z ** 2) ** 0.5
      VM_range = max(VM) - min(VM)
      VM_range_percentile = np.sum(VM_range >= self.activity_distribution) / self.activity_distribution.shape[0]
      VM_range_percentiles.append(VM_range_percentile)
    return {soldier_IDs[i]: VM_range_percentiles[i] for i in range(len(soldier_IDs))}
    
  def optimize_cohort(self, cohort_metadata, cohort_IDs):
    all_outcomes = self.generate_health_predictions(self.squad_metadata, self.soldier_IDs)
    cohort_outcomes = self.generate_health_predictions(cohort_metadata, cohort_IDs)
    self.visualize_cohort(cohort_outcomes)

    cohort_outcomes_class = [i[0] for i in cohort_outcomes.values()]
    num_regular = cohort_outcomes_class.count("regular")
    num_irregular = cohort_outcomes_class.count("irregular")
    num_afib = cohort_outcomes_class.count("afib")

    if num_irregular > 0 or num_afib > 0:
      self.alert_commander(num_irregular, num_afib)
      healthy_replacements = [ID for ID, condition in all_outcomes.items() if condition[0] == "regular" and not ID in cohort_IDs]
      sampled_replacements = np.random.choice(healthy_replacements, size=num_irregular + num_afib, replace=False)
      to_replace = [ID for ID, condition in cohort_outcomes.items() if condition[0] != "regular"]
      for i in to_replace:
        cohort_IDs.remove(i)
      for i in sampled_replacements:
        cohort_IDs.append(i)
      return cohort_IDs
    return cohort_IDs
  
  def optimize_cohort2(self, cohort_metadata, cohort_IDs):
    all_outcomes = self.generate_health_predictions(self.squad_metadata, self.soldier_IDs)
    location_ids = np.random.choice(list(range(len(self.soldier_IDs)//5)), size=len(self.soldier_IDs))
    locations_unique = [(int(1000*np.random.rand()), int(1000*np.random.rand())) for i in range(len(self.soldier_IDs)//5)]
    locations = [locations_unique[i] for i in location_ids]
    loc_temp = (int(1000*np.random.rand()), int(1000*np.random.rand()))
    for i in range(len(self.soldier_IDs)):
      if self.soldier_IDs[i] in cohort_IDs:
        locations[i] = loc_temp
    keys = self.soldier_IDs
    graph_data = {keys[i]:{"location":locations[i], "health":all_outcomes[keys[i]][1]} for i in range(len(keys))}
    location_target = locations_unique[0]
    threshold = 0.9
    target_soldiers = {p: d for p, d in graph_data.items() if tuple(d["location"]) == location_target}
    below_threshold = {p for p, d in target_soldiers.items() if d["health"] < threshold}

    healthy_soldiers = {p: d for p, d in graph_data.items() if d["health"] >= threshold and tuple(d["location"]) != location_target}

    def distance(loc1, loc2):
        return (loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2

    # Greedy algorithm which minimizes the distance that you would have to move healthy troops from other locations to get them to be at location_target
    # The output should be a list of tuples (person_a, person_b), where person_a is the person to be replaced, and person_b is the person replacing them. 
    total_cost = 0
    relocation_plan = []
    for soldier in below_threshold:
        if not healthy_soldiers:
            break  # No more healthy soldiers to move
        
        # Find the closest healthy soldier
        closest_replacement = min(healthy_soldiers, key=lambda s: distance(tuple(healthy_soldiers[s]["location"]), location_target))
        total_cost += distance(tuple(healthy_soldiers[closest_replacement]["location"]), location_target)
        
        # Record the move
        relocation_plan.append((soldier, closest_replacement))
        
        # Remove the moved soldier from available replacements
        del healthy_soldiers[closest_replacement]

    # Output the final relocation plan
    print(relocation_plan)
    print(total_cost)
    
    locations = {tuple(d["location"]) for d in graph_data.values()}
    donor_locations = {tuple(graph_data[p]["location"]) for _, p in relocation_plan}
    # Assign colors based on role
    colors = {}
    for loc in locations:
        if loc == location_target:
            colors[loc] = "green"  # Target location
        elif loc in donor_locations:
            colors[loc] = "red"    # Donor locations
        else:
            colors[loc] = "blue"   # Other locations

    # Plot locations
    plt.figure(figsize=(8, 6))
    for loc, color in colors.items():
        plt.scatter(loc[0], loc[1], color=color, s=200, edgecolors="black", label=color if color not in plt.gca().get_legend_handles_labels()[1] else "")

    # Labels and aesthetics
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Soldier Relocation Visualization")
    plt.legend(["Target (Green)", "Donor (Red)", "Neutral (Blue)"])
    plt.grid(True)
    plt.show()

    # Create NetworkX graph
    G = nx.Graph()

    # Add nodes with colors
    for loc in locations:
        G.add_node(loc, color=colors[loc])

    # Add edges for relocations
    edges = []
    edge_labels = {}
    for donor, receiver in relocation_plan:
        donor_loc = tuple(graph_data[donor]["location"])
        target_loc = tuple(graph_data[receiver]["location"])

        # Ensure the order of the tuple is consistent: donor -> receiver
        edge_tuple = (donor_loc, target_loc) if donor_loc < target_loc else (target_loc, donor_loc)
        
        G.add_edge(donor_loc, target_loc)
        edges.append((donor_loc, target_loc))
        edge_labels[edge_tuple] = edge_labels.get(edge_tuple, "") + f"{donor} → {receiver} "

    # --- Matplotlib Visualization ---
    plt.figure(figsize=(8, 6))
    pos = {loc: loc for loc in locations}  # Position nodes based on coordinates
    node_colors = [colors[n] for n in G.nodes]

    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color="black", node_size=1000, font_size=8, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color="red")

    plt.title("Relocation Graph with Transfers")
    plt.show()

    # --- Pyvis (Interactive Web Visualization) ---
    nt = Network('500px', '500px', notebook=True)
    for node in G.nodes:
        node_id = str(node)  # Convert the tuple to a string
        nt.add_node(node_id, color=colors[node], title=str(node))  # Add tooltips

    # Then, when adding edges to the graph, make sure the correct order is followed:
    for edge in G.edges:
        edge_tuple = (edge[0], edge[1]) if edge[0] < edge[1] else (edge[1], edge[0])
        label = edge_labels.get(edge_tuple, "")
        nt.add_edge(str(edge[0]), str(edge[1]), title=label)  # Ensure edge ordering

    nt.show("nx.html")

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
