"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"

const LineChart = dynamic(() => import("./LineChart"), { ssr: false })

interface SoldierData {
  id: string
  name: string
  age: number
  rank: string
  vitals: {
    heartRate: number[]
    bloodPressure: number[]
    oxygenSaturation: number[]
  }
}

export default function SoldierDetail({ id }: { id: string }) {
  const [soldierData, setSoldierData] = useState<SoldierData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const fetchSoldierData = async () => {
      // In a real application, you would fetch this data from an API
      const mockSoldierData: SoldierData = {
        id,
        name: "John Doe",
        age: 28,
        rank: "Sergeant",
        vitals: {
          heartRate: [70, 72, 75, 73, 71, 74, 76],
          bloodPressure: [120, 122, 118, 121, 119, 123, 120],
          oxygenSaturation: [98, 97, 98, 99, 98, 97, 98],
        },
      }
      setSoldierData(mockSoldierData)
      setIsLoading(false)
    }

    fetchSoldierData()
  }, [id])

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!soldierData) {
    return <div>Soldier not found</div>
  }

  const chartData = {
    labels: ["1m ago", "50s ago", "40s ago", "30s ago", "20s ago", "10s ago", "Now"],
    datasets: [
      {
        label: "Heart Rate",
        data: soldierData.vitals.heartRate,
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.5)",
      },
      {
        label: "Blood Pressure",
        data: soldierData.vitals.bloodPressure,
        borderColor: "rgb(53, 162, 235)",
        backgroundColor: "rgba(53, 162, 235, 0.5)",
      },
      {
        label: "Oxygen Saturation",
        data: soldierData.vitals.oxygenSaturation,
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.5)",
      },
    ],
  }

  return (
    <div className="w-full max-w-4xl">
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <h3 className="text-xl font-bold mb-4">{soldierData.name}</h3>
        <p>
          <strong>ID:</strong> {soldierData.id}
        </p>
        <p>
          <strong>Age:</strong> {soldierData.age}
        </p>
        <p>
          <strong>Rank:</strong> {soldierData.rank}
        </p>
      </div>
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8">
        <LineChart data={chartData} />
      </div>
    </div>
  )
}

