"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Box } from "@mui/material";
import data from "../../subject-data.json"

type SubjectStatus = "Normal" | "Caution" | "Alert";

interface Subject {
  id: string;
  Name: string;
  Age: number;
  Conditions: string;
  Status: SubjectStatus;
  Squad: string;
}

// Define the JSON response type
interface SubjectData {
  Subjects: Record<string, {
    Name: string;
    Age: string; // Stored as a string in JSON, needs conversion
    Conditions: string;
    Squad: string;
  }>;
}

export default function SubjectStatusOverview() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        // Convert object to array and extract required fields
        const mockSubjects: Subject[] = Object.entries(data.Subjects).map(([id, subject]) => ({
          id, // Extract ID from key
          Name: subject.Name,
          Status: determineStatus(subject.Conditions), // Function to derive status if needed
          Squad: subject.Squad,
          Age: Number(subject.Age), // Ensure it's stored as a number
          Conditions: subject.Conditions,
        }));

        console.log("Mock Subjects:", mockSubjects); // ✅ Debugging
        setSubjects(mockSubjects);
      } catch (error) {
        console.error("Error fetching subjects:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSubjects();
  }, []);

  // Function to determine status based on conditions (you can modify this logic)
  const determineStatus = (conditions: string): SubjectStatus => {
    if (conditions.includes("Heart Disease") || conditions.includes("Critical")) return "Alert";
    if (conditions.includes("Hypertension") || conditions.includes("Migraines")) return "Caution";
    return "Normal"; // Default status
  };

  const getStatusColor = (status: SubjectStatus) => {
    switch (status) {
      case "Normal":
        return "bg-green-500";
      case "Caution":
        return "bg-yellow-500";
      case "Alert":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Group subjects by squad
  const squads = subjects.reduce((acc, subject) => {
    if (!acc[subject.Squad]) {
      acc[subject.Squad] = [];
    }
    acc[subject.Squad].push(subject);
    return acc;
  }, {} as Record<string, Subject[]>);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-center mb-4">Squad Overview</h1>
      <div className="space-y-4">
        {Object.entries(squads).map(([squadName, squadMembers]) => (
          <Box key={squadName} className="p-4 border rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-2">{squadName} Squad</h2>
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gray-200">
                  <th className="p-2 text-left">ID</th>
                  <th className="p-2 text-left">Name</th>
                  <th className="p-2 text-center font-semibold w-20">Age</th> 
                  <th className="p-2 text-left">Status</th>
                  <th className="p-2 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {squadMembers.map((subject) => (
                  <tr key={subject.id} className="border-b">
                    <td className="p-2">{subject.id}</td>
                    <td className="p-2">{subject.Name}</td>
                    <td className="p-2 text-center font-normal w-20">{subject.Age}</td> 
                    <td className="p-2">
                      <span className={`inline-block w-3 h-3 rounded-full mr-2 ${getStatusColor(subject.Status)}`}></span>
                      {subject.Status}
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
          </Box>
        ))}
      </div>
    </div>
  );
}
