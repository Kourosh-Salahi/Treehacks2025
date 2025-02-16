"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"

export default function SoldierIdInput() {
  const [soldierId, setSoldierId] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (soldierId) {
      router.push(`/soldier/${soldierId}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center">
      <input
        type="text"
        value={soldierId}
        onChange={(e) => setSoldierId(e.target.value)}
        placeholder="Enter Soldier ID"
        className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        View Soldier Details
      </button>
    </form>
  )
}

