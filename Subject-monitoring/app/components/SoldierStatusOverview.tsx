"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

type SoldierStatus = "Normal" | "Caution" | "Alert"

interface Soldier {
  id: string
  name: string
  status: SoldierStatus
}

export default function SoldierStatusOverview() {
  const [soldiers, setSoldiers] = useState<Soldier[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const fetchSoldiers = async () => {
      // In a real application, you would fetch this data from an API
      const mockSoldiers: Soldier[] = [
        { id: "001", name: "John Doe", status: "Normal" },
        { id: "002", name: "Jane Smith", status: "Caution" },
        { id: "003", name: "Mike Johnson", status: "Alert" },
      ]
      setSoldiers(mockSoldiers)
      setIsLoading(false)
    }

    fetchSoldiers()
  }, [])

  const getStatusColor = (status: SoldierStatus) => {
    switch (status) {
      case "Normal":
        return "bg-green-500"
      case "Caution":
        return "bg-yellow-500"
      case "Alert":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="w-full max-w-4xl">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-200">
            <th className="p-2 text-left">ID</th>
            <th className="p-2 text-left">Name</th>
            <th className="p-2 text-left">Status</th>
            <th className="p-2 text-left">Action</th>
          </tr>
        </thead>
        <tbody>
          {soldiers.map((soldier) => (
            <tr key={soldier.id} className="border-b">
              <td className="p-2">{soldier.id}</td>
              <td className="p-2">{soldier.name}</td>
              <td className="p-2">
                <span className={`inline-block w-3 h-3 rounded-full mr-2 ${getStatusColor(soldier.status)}`}></span>
                {soldier.status}
              </td>
              <td className="p-2">
                <Link href={`/soldier/${soldier.id}`} className="text-blue-600 hover:underline">
                  View Details
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

