import { createContext } from 'react'
import type { LoginCredentials, RegisterData } from '../services/authService'
import type { User } from '../services/types'

export interface AuthState {
  user: User | null
  /** true mientras se recupera la sesión guardada al arrancar. */
  restoring: boolean
  login(credentials: LoginCredentials): Promise<void>
  register(data: RegisterData): Promise<void>
  logout(): void
  /** Solo si la implementación lo ofrece (la demo sí). */
  listDemoUsers?: () => Promise<User[]>
}

// null = se está usando fuera de <AuthProvider> (useAuth lo detecta y avisa).
export const AuthContext = createContext<AuthState | null>(null)
