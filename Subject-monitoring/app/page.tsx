import Link from "next/link"
import dynamic from "next/dynamic"

const SubjectIdInput = dynamic(() => import("./components/SubjectIdInput"), {
  ssr: false,
})

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <h1 className="text-4xl font-bold mb-8">Welcome to Active Subject Monitoring</h1>
      <SubjectIdInput />
      <Link href="/overview" className="mt-4 text-blue-600 hover:underline">
        View Subject Status Overview
      </Link>

      <Link href="/livestream" className="mt-4 text-blue-600 hover:underline">
        View Connected Heartrate Data
      </Link>

      
    </div>
  )
}

