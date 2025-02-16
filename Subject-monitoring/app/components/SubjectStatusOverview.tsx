"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

type SubjectStatus = "Normal" | "Caution" | "Alert"

interface Subject {
  id: string
  name: string
  status: SubjectStatus
}

export default function SubjectStatusOverview() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const fetchSubjects = async () => {
      // In a real application, you would fetch this data from an API
      const mockSubjects: Subject[] = [
        { id: "001", name: "John Doe", status: "Normal" },
        { id: "002", name: "Jane Smith", status: "Caution" },
        { id: "003", name: "Mike Johnson", status: "Alert" },
      ]
      setSubjects(mockSubjects)
      setIsLoading(false)
    }

    fetchSubjects()
  }, [])

  const getStatusColor = (status: SubjectStatus) => {
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
          {subjects.map((subject) => (
            <tr key={subject.id} className="border-b">
              <td className="p-2">{subject.id}</td>
              <td className="p-2">{subject.name}</td>
              <td className="p-2">
                <span className={`inline-block w-3 h-3 rounded-full mr-2 ${getStatusColor(subject.status)}`}></span>
                {subject.status}
              </td>
              <td className="p-2">
                <Link href={`/subject/${subject.id}`} className="text-blue-600 hover:underline">
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

