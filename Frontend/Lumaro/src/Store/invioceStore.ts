import { create } from 'zustand'
import type { Invoice } from '../types'

type InvoiceState = {
  invoices: Invoice[]
  setInvoices: (i: Invoice[]) => void
}

export const useInvoiceStore = create<InvoiceState>((set: (state: Partial<InvoiceState>) => void) => ({
  invoices: [],
  setInvoices: (invoices: Invoice[]) => set({ invoices }),
}))
