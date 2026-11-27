// AuthService con sesión en cookie httpOnly: el cliente nunca maneja el token.
// La sesión se consulta en /auth/me y la cierra el servidor.

import type { AuthService } from './authService'
import { ApiError, http, setUnauthorizedHandler } from './httpClient'
import type { User } from './types'

export function createCookieAuthService(): AuthService {
  const listeners = new Set<() => void>()

  setUnauthorizedHandler(() => listeners.forEach((listener) => listener()))

  return {
    async restoreSession() {
      try {
        return await http.get<User>('/auth/me')
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      }
    },

    login: (credentials) => http.post<User>('/auth/login', credentials),
    register: (data) => http.post<User>('/auth/register', data),

    async logout() {
      await http.post<void>('/auth/logout', {})
    },

    getAuthHeaders: () => ({}), // la cookie la envía el navegador

    onSessionExpired(listener) {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
  }
}
