import ProjectCard from '../Components/ProjectCard'
import { useFetch } from '../Hooks/useFetch'

export default function Projects() {
  const { data, loading } = useFetch('/projects/')
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-heading">Projects</h1>
        <button className="bg-caramel text-white px-4 py-2 rounded">New Project</button>
      </div>
      {loading ? <div>Loading...</div> : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(data || []).map((p:any)=> <ProjectCard key={p.id} project={p} />)}
        </div>
      )}
    </div>
  )
}
