import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './Components/Navbar'
import Sidebar from './Components/Sidebar'
import Dashboard from './Pages/Dashboard'
import Clients from './Pages/Clients'
import Projects from './Pages/Projects'
import ProjectDetails from './Pages/ProjectDetails'
import Invoices from './Pages/Invoices'
import Billing from './Pages/Billing'
import Login from './Pages/Login'
import NotFound from './Pages/NotFound'
// import { useRequireAuth } from './Hooks/useAuth'

export default function App(){
  // simple route guard that redirects to login if not authed
  // useRequireAuth()

  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Navbar />
          <main className="p-6 flex-1 overflow-auto">
            <Routes>
              <Route path="/login" element={<Login/>} />
              <Route path="/" element={<Dashboard/>} />
              <Route path="/clients" element={<Clients/>} />
              <Route path="/projects" element={<Projects/>} />
              <Route path="/projects/:id" element={<ProjectDetails/>} />
              <Route path="/invoices" element={<Invoices/>} />
              <Route path="/billing" element={<Billing/>} />
              <Route path="*" element={<NotFound/>} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
