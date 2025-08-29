import { useEffect } from 'react'
import { useFetch } from '../Hooks/useFetch'
import ClientCard from '../Components/ClientCard'
import ProjectCard from '../Components/ProjectCard'
import InvoiceCard from '../Components/InvoiceCard'
import { useClientStore } from '../Store/clientStore'
import { useProjectStore } from '../Store/projectStore'
import { useInvoiceStore } from '../Store/invioceStore'

export default function Dashboard() {
  const { data: clientsData } = useFetch('/clients/')
  const { data: projectsData } = useFetch('/projects/')
  const { data: invoicesData } = useFetch('/invoices/')
  const setClients = useClientStore((s: any) => s.setClients)
  const setProjects = useProjectStore((s: any) => s.setProjects)
  const setInvoices = useInvoiceStore((s: any) => s.setInvoices)

  useEffect(() => { if (clientsData) setClients(clientsData) }, [clientsData, setClients])
  useEffect(() => { if (projectsData) setProjects(projectsData) }, [projectsData, setProjects])
  useEffect(() => { if (invoicesData) setInvoices(invoicesData) }, [invoicesData, setInvoices])

  return (
    <div>
      <h1 className="text-2xl font-heading text-chocolate mb-4">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <h3 className="font-semibold">Clients</h3>
          <p className="text-3xl mt-2">{clientsData ? clientsData.length : '—'}</p>
        </div>
        <div className="card">
          <h3 className="font-semibold">Active Projects</h3>
          <p className="text-3xl mt-2">{projectsData ? projectsData.filter((p:any)=>p.status!=='completed').length : '—'}</p>
        </div>
        <div className="card">
          <h3 className="font-semibold">Outstanding Invoices</h3>
          <p className="text-3xl mt-2">{invoicesData ? invoicesData.filter((i:any)=>i.status!=='paid').length : '—'}</p>
        </div>
      </div>

      <section className="mt-6">
        <h2 className="text-xl font-heading mb-3">Recent Clients</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(clientsData || []).slice(0,3).map((c:any)=>(<ClientCard key={c.id} client={c}/>))}
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-xl font-heading mb-3">Recent Projects</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(projectsData || []).slice(0,3).map((p:any)=>(<ProjectCard key={p.id} project={p}/>))}
        </div>
      </section>

      <section className="mt-6">
        <h2 className="text-xl font-heading mb-3">Recent Invoices</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(invoicesData || []).slice(0,3).map((i:any)=>(<InvoiceCard key={i.id} invoice={i}/>))}
        </div>
      </section>
    </div>
  )
}
