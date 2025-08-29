import { useState, useEffect } from 'react'
import api from '../Lib/api'

export function useFetch<T = any>(endpoint: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<any>(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    api.get(endpoint)
      .then(res => { if (mounted) setData(res.data) })
      .catch(err => { if (mounted) setError(err) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [endpoint])

  return { data, loading, error }
}
