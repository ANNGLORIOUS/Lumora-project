import { useAuthStore } from "../Store/authStore"

type AuthStore = {
  user: { email: string } | null
  logout: () => void
}

export default function Navbar() {
  const user = useAuthStore((s: AuthStore) => s.user)
  const logout = useAuthStore((s: AuthStore) => s.logout)

  return (
    <header className="h-16 bg-cream border-b border-caramel shadow-sm flex items-center justify-between px-6 ml-64">
      <div className="flex items-center gap-4">
        <div className="text-2xl font-heading text-gold">FreelanceHQ</div>
        <div className="text-sm font-body text-chocolate/80">
          Manage clients, projects & invoices
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-sm text-chocolate">
          {user ? user.email : ""}
        </div>
        <button
          onClick={() => logout()}
          className="bg-caramel px-3 py-1 rounded text-white hover:bg-gold"
        >
          Sign out
        </button>
      </div>
    </header>
  )
}
