// CONTRATO de autenticación: lo que la app necesita de cualquier sistema de login.
//
// Solo tipos, sin implementación (como agent/llm.py en el backend). La app
// (AuthProvider, componentes) depende de esta interfaz y nunca de una
// implementación concreta:
//   - hoy: cookieAuthService.ts → sesión en cookie httpOnly que gestiona el navegador;
//   - otra posible: un token en cabecera `Authorization: Bearer …`.
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
  /** ¿Hay sesión abierta? (al cargar la página). Devuelve el usuario o null. */
  restoreSession(): Promise<User | null>
  login(credentials: LoginCredentials): Promise<User>
  register(data: RegisterData): Promise<User>
  logout(): Promise<void>
  /** Cabeceras extra para cada petición (vacías si la sesión va en una cookie). */
  getAuthHeaders(): Record<string, string>
  /** Avisa cuando la sesión deja de ser válida (p. ej. caduca). Devuelve cómo dejar de escuchar. */
  onSessionExpired(listener: () => void): () => void
}
