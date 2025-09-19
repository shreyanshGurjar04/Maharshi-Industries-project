import React, { useEffect, useState } from "react";
import Sidebar from "../Components/Sidebar";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";
import "./Analytics.css";

export default function Analytics() {
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/detections/")
      .then((res) => res.json())
      .then((data) => setDetections(data))
      .catch((err) => console.error("Error fetching detections:", err));
  }, []);

  // ---- Stats ----
  const totalDetection = detections.length;
  const blacklistAlert = detections.filter((d) => d.blacklist).length;

  // Avg detection per day
  const detectionsPerDay = detections.reduce((acc, det) => {
    const day = new Date(det.timestamp).toLocaleDateString();
    acc[day] = (acc[day] || 0) + 1;
    return acc;
  }, {});

  const avgDetection =
    totalDetection > 0
      ? (totalDetection / Object.keys(detectionsPerDay).length).toFixed(2)
      : 0;

  // Chart data
  const lineData = Object.entries(detectionsPerDay).map(([date, count]) => ({
    date,
    count,
  }));

  const pieData = [
    { name: "Whitelist", value: totalDetection - blacklistAlert },
    { name: "Blacklist", value: blacklistAlert },
  ];

  const COLORS = ["#2ecc71", "#e74c3c"];

  return (
    <>
      <Sidebar />
      <div className="title">
        <h2>Analytics</h2>
      </div>

      <div className="mainBody">
        
        {/* Stats Cards */}
        <div className="statistics">
          <div className="stat-card">
            <h3>Total Detections</h3>
            <p className="data">{totalDetection}</p>
          </div>
          <div className="stat-card">
            <h3>Blacklist Alerts</h3>
            <p className="data"> {blacklistAlert}</p>
          </div>
          <div className="stat-card">
            <h3>Avg Detection/Day</h3>
            <p className="data">{avgDetection}</p>
          </div>
        </div>

        {/* Charts */}
        <div className="charts">
          {/* Line Chart */}
          <div className="chart-card">
            <h3 className="name">Detections per Day</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#3498db" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Pie Chart */}
          <div className="chart-card">
            <h3 className="name">Whitelist vs Blacklist</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </>
  );
}
