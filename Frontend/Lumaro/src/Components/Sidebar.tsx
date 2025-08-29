import { NavLink } from "react-router-dom"

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/clients", label: "Clients" },
  { to: "/projects", label: "Projects" },
  { to: "/invoices", label: "Invoices" },
  { to: "/billing", label: "Billing" },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-[#2B1B17] text-[#FAF3E0] shadow-xl flex flex-col">
      <div className="p-6 border-b border-[#4B3621]">
        <div className="text-xl font-heading text-gold">Workspace</div>
        <div className="text-sm text-[#EADCC7] mt-1">Your tenant</div>
      </div>

      <nav className="flex-1 p-4 flex flex-col gap-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              `px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                isActive
                  ? "bg-[#A97142] text-white shadow-sm"
                  : "text-[#EADCC7] hover:bg-[#4B3621] hover:text-gold"
              }`
            }
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
