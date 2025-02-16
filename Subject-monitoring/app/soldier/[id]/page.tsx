import dynamic from "next/dynamic"

const SoldierDetail = dynamic(() => import("../../components/SubjectDetail"), {
  ssr: false,
})

export default function SoldierPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-8">Soldier Details</h2>
      <SoldierDetail id={params.id} />
    </div>
  )
}

