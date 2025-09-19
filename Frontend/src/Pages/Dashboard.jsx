import Sidebar from "../Components/Sidebar";
import './Dashboard.css';
import React, { useEffect, useState, useRef } from 'react';
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function Dashboard() {
  const [totalDetection, setTotalDetection] = useState(0);
  const [blacklistAlert, setBlacklistAlert] = useState(0);
  const lastDetections = useRef([]);
  const isInitialLoad = useRef(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const totalRes = await fetch("http://127.0.0.1:8000/api/detections/");
        const totalData = await totalRes.json();

        if (totalRes.status === 304) {
          toast.success("Existing detections (304)", {
            position: "top-right",
            autoClose: 3000,
            style: { backgroundColor: "green", color: "white" },
          });
          return; 
        }

        setTotalDetection(totalData.length);

        const blacklistCount = totalData.filter(det => det.is_blacklist).length;
        setBlacklistAlert(blacklistCount);

        if (!isInitialLoad.current) {
          const newDetections = totalData.filter(
            det => !lastDetections.current.includes(det.id)
          );

          newDetections.forEach(det => {
            if (det.is_blacklist) {
              // Red toast for blacklist
              toast.error(`Blacklist detected: ${det.no_plate}`, {
                position: "top-right",
                autoClose: 5000,
                style: { backgroundColor: "red", color: "white" },
              });
            } else {
              // Blue toast for normal new detection
              toast.info(`New detection: ${det.no_plate}`, {
                position: "top-right",
                autoClose: 5000,
                style: { backgroundColor: "blue", color: "white" },
              });
            }
          });
        } else {
          isInitialLoad.current = false;
        }

        lastDetections.current = totalData.map(det => det.id);

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Sidebar />
      <div className="title">
        <h2>Dashboard</h2>
      </div>
      <div className="Body1">
        <div className="box TotalDetection">
          <div className="txt">
            <h2 className="Detect">{totalDetection}</h2>
            <h4>Total Detection</h4>
          </div>
        </div>

        <div className="box Alerts">
          <div className="txt">
            <h2 className="alert">{blacklistAlert}</h2>
            <h4>BlackList Alert</h4>
          </div>
        </div>

        <div className="box Avg">
          <div className="txt">
            <h2 className="average">
              {totalDetection > 0 ? (totalDetection / 3600).toFixed(2) : 0}
            </h2>
            <h4 className="av">Avg. Detection (per hour)</h4>
          </div>
        </div>
      </div>

      <div className="LiveFeed">
        <h2>Live Feed</h2>
        <img
          className="feed"
          src="http://127.0.0.1:8000/api/video_feed/"
          alt="Live Feed"
          style={{ width: "100%", border: "2px solid black" }}
        />
      </div>

      <ToastContainer />
    </>
  )
}
