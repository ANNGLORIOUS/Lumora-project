import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, loadAuthFromStorage } from '../Store/authStore'

export function useAuth() {
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) {
      const stored = loadAuthFromStorage()
      if (stored && stored.user && stored.token) {
        setUser(stored.user, stored.token)
      } else {
        navigate('/login')
      }
    }
  }, [user, setUser, navigate])
}
