// CONTRATO de autenticación: lo que la app necesita de cualquier sistema de login.
//
// Solo tipos, sin implementación (como agent/llm.py en el backend). La app
// (AuthContext, componentes) depende de esta interfaz y nunca de una
// implementación concreta:
//   - hoy:    demoAuthService.ts → elegir un cliente de prueba, cabecera X-User-Id;
//   - mañana: p. ej. jwtAuthService.ts → POST /auth/login, `Authorization: Bearer …`.
// Cambiar de una a otra es tocar una línea en main.tsx.

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
  /** Recupera la sesión guardada (p. ej. al recargar la página), o null. */
  restoreSession(): Promise<User | null>
  login(credentials: LoginCredentials): Promise<User>
  register(data: RegisterData): Promise<User>
  logout(): void
  /** Cabeceras que identifican al usuario en cada petición al backend. */
  getAuthHeaders(): Record<string, string>
  /** Opcional, solo en la demo: clientes para entrar con un clic. */
  listDemoUsers?(): Promise<User[]>
}
