import { create } from 'zustand'
import type { User } from '../types'

type AuthState = {
  user: User | null
  token: string | null
  setUser: (user: User, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set: (partial: Partial<AuthState>) => void) => ({
  user: null,
  token: null,
  setUser: (user: User, token: string) => {
    localStorage.setItem('freelancehq_auth', JSON.stringify({ user, token }))
    set({ user, token })
  },
  logout: () => {
    localStorage.removeItem('freelancehq_auth')
    set({ user: null, token: null })
  }
}))

export const getAuthToken = () => {
  try {
    const raw = localStorage.getItem('freelancehq_auth')
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return parsed.token || null
  } catch (e) { return null }
}

export const loadAuthFromStorage = () => {
  try {
    const raw = localStorage.getItem('freelancehq_auth')
    if (!raw) return null
    return JSON.parse(raw)
  } catch (e) { return null }
}
