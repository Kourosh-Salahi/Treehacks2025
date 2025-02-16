"use client";

import React from "react";

const jsonUrl = "https://2394-68-65-164-17.ngrok-free.app/backfill"; // Ngrok URL

export default function HeartrateStream() {
  return (
    <div className="max-w-3xl mx-auto p-6 bg-white shadow-md rounded-lg">
      <h1 className="text-xl font-bold mb-4">Terra Json:</h1>
      <div className="border rounded-md overflow-hidden">
        <iframe
          src={jsonUrl}
          width="100%"
          height="600px"
          className="border-none"
        ></iframe>
      </div>
    </div>
  );
}
