import Sidebar from "../Components/Sidebar";
import './WhiteList.css';
import React, { useEffect, useState } from 'react';

export default function WhiteList() {
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/Whitelist/") 
      .then((res) => res.json())
      .then((data) => setDetections(data))
      .catch((err) => console.error("Error fetching detections:", err));
  }, []);

  // ✅ Filter only whitelist detections (blacklist = false)
  const whiteListDetections = detections.filter((det) => !det.blacklist);

  return (
    <>
      <Sidebar />
      <div className="title">
        <h2>WhiteList</h2>
      </div>
      <div className="Body1">
        {whiteListDetections.length === 0 ? (
          <p>No whitelist detections found.</p>
        ) : (
          <div className="detections-grid">
            {whiteListDetections.map((det) => (
              <div className="detection-card" key={det.id}>
                <img
                  src={`http://127.0.0.1:8000/${det.image_path}`}
                  alt={`Plate ${det.no_plate}`}
                  className="detection-img"
                />
                <p className="plate-number">
                  Plate: <strong>{det.no_plate}</strong>
                </p>
                <p className="timestamp">
                  Time: {new Date(det.timestamp).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
