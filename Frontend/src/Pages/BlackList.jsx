import Sidebar from "../Components/Sidebar";
import './BlackList.css';
import React, { useState, useEffect } from 'react';


export default function BlackList() {
  const [detections, setDetections] = useState([]);
  
    useEffect(() => {
      fetch("http://127.0.0.1:8000/api/Blacklist/") 
        .then((res) => res.json())
        .then((data) => setDetections(data))
        .catch((err) => console.error("Error fetching detections:", err));
    }, []);
  

    const whiteListDetections = detections.filter((det) => det.blacklist);
  return (
    <>
        <Sidebar/>
         <div className="title">
        <h2>BlackList</h2>
      </div>
      <div className="Body1">
        {whiteListDetections.length === 0 ? (
          <p>No BlackList detections found.</p>
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
    
  )
}
