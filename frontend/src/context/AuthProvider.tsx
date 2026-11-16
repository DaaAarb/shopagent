import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { AuthService, LoginCredentials, RegisterData } from '../services/authService'
import type { User } from '../services/types'
import { AuthContext, type AuthState } from './AuthContext'

interface Props {
  // Inyección de dependencias: el proveedor no sabe QUÉ sistema de login hay
  // detrás, solo que cumple la interfaz AuthService. Lo decide main.tsx.
  service: AuthService
  children: ReactNode
}

/** Guarda quién ha iniciado sesión y lo comparte con toda la app (React Context). */
export function AuthProvider({ service, children }: Props) {
  const [user, setUser] = useState<User | null>(null)
  const [restoring, setRestoring] = useState(true)

  useEffect(() => {
    service
      .restoreSession()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setRestoring(false))
  }, [service])

  const login = useCallback(
    async (credentials: LoginCredentials) => setUser(await service.login(credentials)),
    [service],
  )
  const register = useCallback(
    async (data: RegisterData) => setUser(await service.register(data)),
    [service],
  )
  const logout = useCallback(() => {
    service.logout()
    setUser(null)
  }, [service])

  // useMemo: el objeto solo cambia si cambia algo de dentro. Si se creara uno
  // nuevo en cada render, todos los componentes que usan el contexto se
  // volverían a pintar sin necesidad.
  const value = useMemo<AuthState>(
    () => ({
      user,
      restoring,
      login,
      register,
      logout,
      listDemoUsers: service.listDemoUsers?.bind(service),
    }),
    [user, restoring, login, register, logout, service],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
