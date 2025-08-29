
import type { Invoice } from '../types'

export default function InvoiceCard({ invoice }: { invoice: Invoice }) {
  return (
    <div className="card flex justify-between items-center">
      <div>
        <div className="font-heading text-chocolate">{invoice.invoice_number}</div>
        <div className="text-sm text-chocolate/70">Status: {invoice.status}</div>
      </div>
      <div className="font-bold text-chocolate">KES {invoice.total}</div>
    </div>
  )
}
