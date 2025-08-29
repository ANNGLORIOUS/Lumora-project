import { create } from 'zustand'
import type { Client } from '../types'

type ClientState = {
  clients: Client[]
  setClients: (c: Client[]) => void
}

export const useClientStore = create<ClientState>((set: (state: Partial<ClientState>) => void) => ({
  clients: [],
  setClients: (clients: Client[]) => set({ clients }),
}))
