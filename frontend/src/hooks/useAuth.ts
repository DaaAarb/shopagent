import { useContext } from 'react'
import { AuthContext, type AuthState } from '../context/AuthContext'

export function useAuth(): AuthState {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth debe usarse dentro de <AuthProvider>.')
  return auth
}
