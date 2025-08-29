import { Link } from 'react-router-dom'

export default function NotFound(){
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-heading text-chocolate mb-2">404</h1>
      <p className="text-chocolate/70 mb-4">Page not found</p>
      <Link to="/" className="bg-caramel text-white px-4 py-2 rounded">Go Home</Link>
    </div>
  )
}
