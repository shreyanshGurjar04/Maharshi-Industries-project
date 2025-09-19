import React, { useEffect, useState } from 'react';
import Sidebar from '../Components/Sidebar';
import './VideoPlay.css';

export default function VideoPlay() {
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/detections/") // fetch all detections
      .then((res) => res.json())
      .then((data) => setDetections(data))
      .catch((err) => console.error("Error fetching detections:", err));
  }, []);

  // Filter detections that have videos
  const detectionsWithVideos = detections.filter(det => det.video_path);

  return (
    <>
      <Sidebar />
      <div className="title">
        <h2>Video Playback</h2>
      </div>
      <div className="Body1">
        {detectionsWithVideos.length === 0 ? (
          <p>No video playback found.</p>
        ) : (
          <div className="detections-grid">
            {detectionsWithVideos.map((det) => (
              <div className="detection-card" key={det.id}>
                {det.video_path && (
                  <video
                    src={`http://127.0.0.1:8000/${det.video_path}`}
                    controls
                    className="detection-video"
                  />
                )}
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
