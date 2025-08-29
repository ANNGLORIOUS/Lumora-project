
import type { Task } from '../types'

export default function TaskCard({ task }: { task: Task }) {
  return (
    <div className="bg-white p-3 rounded shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <div className="font-semibold text-chocolate">{task.title}</div>
          <div className="text-sm text-chocolate/70">Priority: {task.priority}</div>
        </div>
        <div className="text-sm text-chocolate/80">{task.status}</div>
      </div>
    </div>
  )
}
