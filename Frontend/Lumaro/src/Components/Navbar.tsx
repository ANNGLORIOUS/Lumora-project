import { useAuthStore } from "../Store/authStore"

type AuthStore = {
  user: { email: string } | null
  logout: () => void
}

export default function Navbar() {
  const user = useAuthStore((s: AuthStore) => s.user)
  const logout = useAuthStore((s: AuthStore) => s.logout)

  return (
    <header className="fixed top-0 left-0 w-full h-16 bg-[#2B1B17] text-[#FAF3E0] flex items-center justify-between px-6 border-b border-[#4B3621] shadow-md z-50">
      <div className="flex items-center gap-4">
        <div className="text-2xl font-heading text-gold">FreelanceHQ</div>
        <div className="text-sm font-body text-[#D2B48C]">
          Manage clients, projects & invoices
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user && <div className="text-sm text-[#EADCC7]">{user.email}</div>}
        <button
          onClick={() => logout()}
          className="bg-[#A97142] hover:bg-[#D4AF37] text-white px-4 py-2 rounded-md transition"
        >
          Sign out
        </button>
      </div>
    </header>
  )
}
