import React from "react";

const ImageGallery: React.FC = () => {
  return (
    <div>
      <h2>Soldier Relocation Visualization</h2>

      {/* Plot Image */}
      <h3>Plot</h3>
      <img src="http://127.0.0.1:5000/plot" alt="Soldier Plot" width="600" />

      {/* Interactive Network Graph */}
      <h3>Network Graph</h3>
      <iframe
        src="http://127.0.0.1:5000/network"
        title="Network Graph"
        width="800"
        height="600"
        style={{ border: "none" }}
      />

      {/* Relocation Plan (Interactive Pyvis Graph) */}
      <h3>Relocation Plan</h3>
      <iframe
        src="http://127.0.0.1:5000/relocation"
        title="Relocation Plan"
        width="800"
        height="600"
        style={{ border: "none" }}
      />
    </div>
  );
};

export default ImageGallery;
