import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { AuthService, LoginCredentials, RegisterData } from '../services/authService'
import type { User } from '../services/types'
import { AuthContext, type AuthState } from './AuthContext'

interface Props {
  // Implementación concreta elegida en main.tsx.
  service: AuthService
  children: ReactNode
}

export function AuthProvider({ service, children }: Props) {
  const [user, setUser] = useState<User | null>(null)
  const [restoring, setRestoring] = useState(true)
  const [expired, setExpired] = useState(false)

  useEffect(() => {
    service
      .restoreSession()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setRestoring(false))
  }, [service])

  // Sesión caducada durante el uso: vuelta al login con aviso.
  useEffect(
    () =>
      service.onSessionExpired(() => {
        setUser(null)
        setExpired(true)
      }),
    [service],
  )

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      setUser(await service.login(credentials))
      setExpired(false)
    },
    [service],
  )
  const register = useCallback(
    async (data: RegisterData) => {
      setUser(await service.register(data))
      setExpired(false)
    },
    [service],
  )
  const logout = useCallback(async () => {
    try {
      await service.logout()
    } finally {
      setUser(null) // se cierra la sesión local aunque falle la red
    }
  }, [service])

  const value = useMemo<AuthState>(
    () => ({ user, restoring, expired, login, register, logout }),
    [user, restoring, expired, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
