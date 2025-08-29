import Sidebar from "../Components/Sidebar"
import Navbar from "../Components/Navbar"

type LayoutProps = {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="h-screen bg-[#FAF3E0]">
      {/* Navbar fixed at top */}
      <Navbar />

      <div className="flex">
        {/* Sidebar fixed on left, below navbar */}
        <Sidebar />

        {/* Main content wrapper */}
        <main className="flex-1 pt-16 pl-64 p-6 overflow-y-auto text-[#2B1B17]">
          {children}
        </main>
      </div>
    </div>
  )
}
