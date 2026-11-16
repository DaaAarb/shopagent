import { useCallback, useEffect, useState } from 'react'

interface ApiState<T> {
  data: T | null
  error: string | null
  loading: boolean
  reload: () => void
}

/**
 * Hook propio: carga datos al montar el componente (y cuando cambian `deps`).
 *
 * Un hook es una función que usa otros hooks (useState, useEffect…). Sirve
 * para reutilizar lógica con estado: cada componente que lo llama tiene su
 * propia copia de `data`, `error` y `loading`.
 */
export function useApi<T>(load: () => Promise<T>, deps: unknown[] = []): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [version, setVersion] = useState(0)

  useEffect(() => {
    // Si el componente se desmonta o cambian las dependencias antes de que
    // llegue la respuesta, se ignora: evita pintar datos que ya no tocan.
    let ignore = false
    setLoading(true)
    setError(null)
    load()
      .then((result) => !ignore && setData(result))
      .catch((err: Error) => !ignore && setError(err.message))
      .finally(() => !ignore && setLoading(false))
    return () => {
      ignore = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, version])

  const reload = useCallback(() => setVersion((v) => v + 1), [])
  return { data, error, loading, reload }
}
