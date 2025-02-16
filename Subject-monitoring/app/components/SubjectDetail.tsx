"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import data from "../../subject-data.json";

const LineChart = dynamic(() => import("./LineChart"), { ssr: false });

interface SubjectVitals {
  HeartRate: number[];
  Green: number[];
  Red: number[];
  IR: number[];
  "X-acceleration": number[];
  "Y-acceleration": number[];
  "Z-acceleration": number[];
}

interface Subject {
  Name: string;
  Age: string;
  Conditions: string;
  Squad: string;
  Vitals: SubjectVitals;
}

interface SubjectsData {
  [key: string]: Subject;
}

const subjects: SubjectsData = data.Subjects;

export default function SubjectDetail({ id }: { id: string }) {
  const [subjectData, setSubjectData] = useState<Subject | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSubjectData = async () => {
      const subject = subjects[id];

      if (!subject) {
        setSubjectData(null);
      } else {
        setSubjectData(subject);
      }
      setIsLoading(false);
    };

    fetchSubjectData();
  }, [id]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!subjectData) {
    return <div>Subject not found</div>;
  }

  const chartData = {
    labels: ["1m ago", "50s ago", "40s ago", "30s ago", "20s ago", "10s ago", "Now"],
    datasets: [
      {
        label: "Heart Rate",
        data: subjectData.Vitals.HeartRate,
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.5)",
        hidden: false, // Heart Rate is visible by default
      },
      {
        label: "Green",
        data: subjectData.Vitals.Green,
        borderColor: "rgb(0, 255, 0)",
        backgroundColor: "rgba(0, 255, 0, 0.5)",
        hidden: true, // Initially hidden
      },
      {
        label: "Red",
        data: subjectData.Vitals.Red,
        borderColor: "rgb(255, 0, 0)",
        backgroundColor: "rgba(255, 0, 0, 0.5)",
        hidden: true, // Initially hidden
      },
      {
        label: "IR",
        data: subjectData.Vitals.IR,
        borderColor: "rgb(128, 0, 128)",
        backgroundColor: "rgba(128, 0, 128, 0.5)",
        hidden: true, // Initially hidden
      },
      {
        label: "X-Acceleration",
        data: subjectData.Vitals["X-acceleration"],
        borderColor: "rgb(0, 0, 255)",
        backgroundColor: "rgba(0, 0, 255, 0.5)",
        hidden: true, // Initially hidden
      },
      {
        label: "Y-Acceleration",
        data: subjectData.Vitals["Y-acceleration"],
        borderColor: "rgb(255, 165, 0)",
        backgroundColor: "rgba(255, 165, 0, 0.5)",
        hidden: true, // Initially hidden
      },
      {
        label: "Z-Acceleration",
        data: subjectData.Vitals["Z-acceleration"],
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        hidden: true, // Initially hidden
      },
    ],
  };

  return (
    <div className="w-full max-w-4xl">
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <h3 className="text-xl font-bold mb-4">{subjectData.Name}</h3>
        <p>
          <strong>ID:</strong> {id}
        </p>
        <p>
          <strong>Age:</strong> {subjectData.Age}
        </p>
        <p>
          <strong>Conditions:</strong> {subjectData.Conditions}
        </p>
        <p>
          <strong>Squad:</strong> {subjectData.Squad}
        </p>
      </div>
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8">
        <LineChart data={chartData} />
      </div>
    </div>
  );
}
