import React, { useEffect, useState } from "react";
import Sidebar from "../Components/Sidebar";
import "./Detection.css";

export default function Detection() {
  const [detections, setDetections] = useState([]);

  const [filters, setFilters] = useState({
    plate: "",
    start_date: "",
    end_date: "",
    blacklist: ""
  });

  const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const fetchSearch = () => {
    const query = new URLSearchParams(filters).toString();
    fetch(`http://127.0.0.1:8000/api/search-detections/?${query}`)
      .then((res) => res.json())
      .then((data) => setDetections(data))
      .catch((err) => console.error("Error fetching detections:", err));
  };

  useEffect(() => {
    fetchDetections();
  }, []);

  const fetchDetections = () => {
    fetch("http://127.0.0.1:8000/api/detections/")
      .then((res) => res.json())
      .then((data) => setDetections(data))
      .catch((err) => console.error("Error fetching detections:", err));
  };

  const handleToggleBlacklist = (detId, currentValue) => {
    fetch(`http://127.0.0.1:8000/api/detections/${detId}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ blacklist: !currentValue }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to update blacklist");
        return res.json();
      })
      .then((updatedDet) => {
        setDetections((prev) =>
          prev.map((det) => (det.id === detId ? updatedDet : det))
        );
      })
      .catch((err) => console.error("Error updating blacklist:", err));
  };

  const handleDeleteDetection = (detId) => {
    fetch(`http://127.0.0.1:8000/api/detections/${detId}/`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete detection");
        setDetections((prev) => prev.filter((det) => det.id !== detId));
      })
      .catch((err) => console.error("Error deleting detection:", err));
  };

  const handlePDF = () => {
    fetch('http://127.0.0.1:8000/api/Report-pdf/', {
      method: "GET"
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch PDF");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;

        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
        link.setAttribute('download', `detections_${timestamp}.pdf`);

        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      })
      .catch(err => console.error("Error downloading PDF:", err));
  };

  const handleCSV = () => {
    fetch('http://127.0.0.1:8000/api/Report-csv/', {
      method: "GET"
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch CSV");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;

        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
        link.setAttribute('download', `detections_${timestamp}.csv`);

        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      })
      .catch(err => console.error("Error downloading CSV:", err));
  };

  return (
    <>
      <Sidebar />
      <div className="title">
        <h2>Detection</h2>
      </div>

      <div className="filters">
        <input
          type="text"
          name="plate"
          placeholder="Plate number"
          value={filters.plate}
          onChange={handleChange}
        />

        <input

          type="date"
          name="start_date"
          value={filters.start_date}
          onChange={handleChange}
        />
        <input
          type="date"
          name="end_date"
          value={filters.end_date}
          onChange={handleChange}
        />

        <select
          name="blacklist"
          value={filters.blacklist}
          onChange={handleChange}
        >
          <option value="">All</option>
          <option value="true">Blacklisted</option>
          <option value="false">Whitelist</option>
        </select>

        <button className="btnn" onClick={fetchSearch}>Search</button>
        <button className="btnn" onClick={handleCSV}>Export CSV</button>
        <button className="btnn" onClick={handlePDF}>Export PDF</button>
      </div>

      <div className="Body1">
        {detections.length === 0 ? (
          <p>No detections found.</p>
        ) : (
          <div className="detections-grid">
            {detections.map((det) => (
              <div className="detection-card" key={det.id}>
                {det.image_path && (
                  <img
                    src={`http://127.0.0.1:8000/${det.image_path}`}
                    alt={`Plate ${det.no_plate}`}
                    className="detection-img"
                  />
                )}
                <p className="plate-number">
                  Plate: <strong>{det.no_plate}</strong>
                </p>
                <p className="timestamp">
                  Time Stamp:{" "}
                  <strong>{new Date(det.timestamp).toLocaleString()}</strong>
                </p>
                <div className="toggle-btn">
                  <div className="toggle">
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={det.blacklist}
                        onChange={() =>
                          handleToggleBlacklist(det.id, det.blacklist)
                        }
                      />
                      <span className="slider"></span>
                    </label>
                    <span className="toggle-label">
                      {det.blacklist ? "Blacklisted" : "Whitelist"}
                    </span>
                  </div>

                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteDetection(det.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
