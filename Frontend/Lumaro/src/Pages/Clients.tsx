import { Link } from 'react-router-dom'
import { useFetch } from '../Hooks/useFetch'
import ClientCard from '../Components/ClientCard'

export default function Clients() {
  const { data, loading } = useFetch('/clients/')

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-heading">Clients</h1>
        <Link to="/clients/new" className="bg-caramel text-white px-4 py-2 rounded">New Client</Link>
      </div>
      {loading ? <div>Loading...</div> : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(data || []).map((c:any)=> <ClientCard key={c.id} client={c} />)}
        </div>
      )}
    </div>
  )
}
