import { useContext } from 'react'
import { AuthContext, type AuthState } from '../context/AuthContext'

/** Acceso a la sesión desde cualquier componente: `const { user, logout } = useAuth()`. */
export function useAuth(): AuthState {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth debe usarse dentro de <AuthProvider>.')
  return auth
}
