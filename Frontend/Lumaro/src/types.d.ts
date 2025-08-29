export type User = { id: number; email: string; name?: string }
export type Tenant = { id: number; name: string; subdomain?: string }
export type Client = { id: number; tenant: number; name: string; email?: string; phone?: string; company?: string }
export type Project = { id: number; tenant: number; client: number; name: string; status: string; start_date?: string; end_date?: string }
export type Task = { id: number; project: number; title: string; status: string; priority: number }
export type Invoice = { id: number; invoice_number: string; client: number; total: number; status: string }
