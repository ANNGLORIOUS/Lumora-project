import { useFetch } from '../Hooks/useFetch'
import InvoiceCard from '../Components/InvoiceCard'

export default function Invoices() {
  const { data, loading } = useFetch('/invoices/')
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-heading">Invoices</h1>
        <button className="bg-caramel text-white px-4 py-2 rounded">New Invoice</button>
      </div>
      {loading ? <div>Loading...</div> : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(data || []).map((i:any)=> <InvoiceCard key={i.id} invoice={i} />)}
        </div>
      )}
    </div>
  )
}
