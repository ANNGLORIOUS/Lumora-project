import Sidebar from "../Components/Sidebar"
import Navbar from "../Components/Navbar"

type LayoutProps = {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen bg-cream">
      {/* Sidebar fixed left */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex flex-col flex-1 ml-64">
        {/* Navbar stays at top */}
        <Navbar />

        {/* Scrollable page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
