  "use client";

  import HeartRateStream from "../components/HeartrateStream"; // Use one consistent import

  export default function LiveStreamPage() {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold mb-4">📡 Live Heart Rate Data</h1>
        <HeartRateStream /> {/* Use the correct component name */}
      </div>
    );
  }
