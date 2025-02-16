"use client";

import React, { useEffect, useState } from "react";

const TERRA_WS_URL = "wss://ws.terraapi.io"; // Replace if needed
const TERRA_API_TOKEN = "temp"; // Replace with your actual API token

const HeartRateStream: React.FC = () => {
  const [heartRate, setHeartRate] = useState<number | null>(null);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    const socket = new WebSocket(TERRA_WS_URL);
    let heartbeatInterval: NodeJS.Timeout;

    socket.addEventListener("open", () => {
      console.log("✅ Connected to Terra WebSocket");
      setConnected(true);

      // Authenticate with Terra
      const identifyPayload = {
        op: 3,
        d: {
          token: TERRA_API_TOKEN,
          type: 0,
        },
      };
      socket.send(JSON.stringify(identifyPayload));
    });

    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      console.log("📩 Received:", message);

      if (message.op === 2) {
        // Start Heartbeat
        const interval = message.d.heartbeat_interval;
        heartbeatInterval = setInterval(() => {
          socket.send(JSON.stringify({ op: 0 }));
        }, interval);
      }

      if (message.op === 4) {
        console.log("✅ Authentication Successful");
      }

      if (message.op === 5 && message.t === "HEART_RATE") {
        setHeartRate(message.d.val);
      }
    });

    socket.addEventListener("close", () => {
      console.log("❌ Disconnected from Terra WebSocket");
      setConnected(false);
    });

    return () => {
      clearInterval(heartbeatInterval);
      socket.close();
    };
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-lg">
      <h2 className="text-xl font-semibold mb-2">Real-Time Heart Rate</h2>
      {connected ? (
        <p className="text-lg">
          {heartRate !== null ? (
            <span className="font-bold text-red-600">{heartRate} BPM</span>
          ) : (
            "Waiting for data..."
          )}
        </p>
      ) : (
        <p className="text-gray-500">🔄 Connecting to Terra...</p>
      )}
    </div>
  );
};

export default HeartRateStream;
