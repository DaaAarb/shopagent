import { createContext } from 'react'
import type { LoginCredentials, RegisterData } from '../services/authService'
import type { User } from '../services/types'

export interface AuthState {
  user: User | null
  /** true mientras se comprueba si ya había sesión al arrancar. */
  restoring: boolean
  /** true si se volvió al login porque la sesión caducó (para avisar al usuario). */
  expired: boolean
  login(credentials: LoginCredentials): Promise<void>
  register(data: RegisterData): Promise<void>
  logout(): Promise<void>
}

// null fuera de <AuthProvider>; useAuth lo detecta.
export const AuthContext = createContext<AuthState | null>(null)
