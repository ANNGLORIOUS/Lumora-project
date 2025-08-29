import { useForm } from 'react-hook-form'
import api from '../Lib/api'
import { useAuthStore } from '../Store/authStore'
import { useNavigate } from 'react-router-dom'

type Form = { email: string; password: string }

export default function Login() {
  const { register, handleSubmit } = useForm<Form>()
  const setUser = useAuthStore((s: { setUser: (user: any, token: string) => void }) => s.setUser)
  const navigate = useNavigate()
  const onSubmit = async (data: Form) => {
    try {
      const res = await api.post('/auth/login/', data)
      // Expect backend to return { user: {...}, token: '...' }
      setUser(res.data.user, res.data.token)
      navigate('/')
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-cream">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-heading text-chocolate mb-6">Sign in</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <input {...register('email')} placeholder="Email" className="w-full border border-caramel rounded px-4 py-2" />
          <input {...register('password')} type="password" placeholder="Password" className="w-full border border-caramel rounded px-4 py-2" />
          <button type="submit" className="w-full bg-caramel text-white py-2 rounded hover:bg-gold">Sign in</button>
        </form>
      </div>
    </div>
  )
}
