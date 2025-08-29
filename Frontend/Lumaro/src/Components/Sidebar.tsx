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
    <aside className="fixed left-0 top-0 h-screen w-64 bg-chocolate text-cream shadow-lg flex flex-col">
      <div className="p-6 border-b border-caramel">
        <div className="text-xl font-heading text-gold">Workspace</div>
        <div className="text-sm text-cream/70 mt-1">Your tenant</div>
      </div>
      <nav className="flex-1 p-4 flex flex-col gap-2">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              `px-3 py-2 rounded-md transition ${
                isActive
                  ? "bg-caramel text-white"
                  : "text-cream hover:bg-gold/20"
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
