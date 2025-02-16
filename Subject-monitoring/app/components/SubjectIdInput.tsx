"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"

export default function SubjectIdInput() {
  const [subjectId, setSubjectId] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (subjectId) {
      router.push(`/subject/${subjectId}`)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center">
      <input
        type="text"
        value={subjectId}
        onChange={(e) => setSubjectId(e.target.value)}
        placeholder="Enter Subject ID"
        className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        View Subject Details
      </button>
    </form>
  )
}

