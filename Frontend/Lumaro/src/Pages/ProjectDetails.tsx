import { useParams } from 'react-router-dom'
import { useFetch } from '../Hooks/useFetch'
import TaskCard from '../Components/TaskCard'

export default function ProjectDetails() {
  const { id } = useParams()
  const { data, loading } = useFetch(`/projects/${id}/`)

  if (loading) return <div>Loading...</div>
  if (!data) return <div>Project not found</div>

  return (
    <div>
      <h1 className="text-2xl font-heading mb-4">{data.name}</h1>
      <p className="text-sm text-chocolate/70 mb-4">{data.description}</p>
      <h2 className="font-semibold mb-2">Tasks</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {(data.tasks || []).map((t:any)=>(<TaskCard key={t.id} task={t}/>))}
      </div>
    </div>
  )
}
