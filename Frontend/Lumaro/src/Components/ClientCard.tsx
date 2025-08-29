
import type { Client } from '../types'

export default function ClientCard({ client }: { client: Client }) {
  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-heading text-chocolate">{client.name}</h3>
          <div className="text-sm text-chocolate/70">{client.company || client.email}</div>
        </div>
      </div>
    </div>
  )
}
