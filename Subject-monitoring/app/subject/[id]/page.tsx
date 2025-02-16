import dynamic from "next/dynamic"

const SubjectDetail = dynamic(() => import("../../components/SubjectDetail"), {
  ssr: false,
})

export default function SubjectPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-8">Subject Details</h2>
      <SubjectDetail id={params.id} />
    </div>
  )
}

