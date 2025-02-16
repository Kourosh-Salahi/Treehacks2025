"use client";

import HeartRateStream from "../components/HeartrateStream";

export default function LiveStreamPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl font-bold mb-4">📡 Live Heart Rate Stream</h1>
      <HeartRateStream />
    </div>
  );
}
