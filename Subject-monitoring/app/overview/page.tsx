import dynamic from "next/dynamic"

const SubjectStatusOverview = dynamic(() => import("../components/SubjectStatusOverview"), {
  ssr: false,
})

export default function Overview() {
  return (
    <div className="flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-8">Subject Status Overview</h2>
      <SubjectStatusOverview />
    </div>
  )
}

