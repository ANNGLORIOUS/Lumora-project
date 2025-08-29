
import type { Project } from '../types'

export default function ProjectCard({ project }: { project: Project }) {
  return (
    <div className="card">
      <div className="flex justify-between">
        <div>
          <h3 className="font-heading text-chocolate">{project.name}</h3>
          <div className="text-sm text-chocolate/70">Status: {project.status}</div>
        </div>
      </div>
    </div>
  )
}
