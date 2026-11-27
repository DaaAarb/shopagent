// Contrato de autenticación. La app depende de esta interfaz, no de una implementación
// concreta (hoy cookieAuthService.ts); se elige en main.tsx.

import type { User } from './types'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
}

export interface AuthService {
  /** Usuario de la sesión actual, o null si no hay sesión. */
  restoreSession(): Promise<User | null>
  login(credentials: LoginCredentials): Promise<User>
  register(data: RegisterData): Promise<User>
  logout(): Promise<void>
  /** Cabeceras extra para cada petición (vacías si la sesión va en una cookie). */
  getAuthHeaders(): Record<string, string>
  /** Notifica cuando la sesión deja de ser válida. Devuelve la función para desuscribirse. */
  onSessionExpired(listener: () => void): () => void
}
