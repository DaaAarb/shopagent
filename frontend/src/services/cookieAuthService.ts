// Implementación del contrato AuthService con sesión en cookie httpOnly.
//
// El backend guarda la sesión (un JWT firmado) en una cookie que el JavaScript
// NO puede leer. Por eso aquí no se guarda ningún token: el navegador manda la
// cookie solo en cada petición a /api. Para saber si hay sesión se pregunta a
// /auth/me, y para cerrarla se pide al servidor que borre la cookie.

import type { AuthService } from './authService'
import { ApiError, http, setUnauthorizedHandler } from './httpClient'
import type { User } from './types'

export function createCookieAuthService(): AuthService {
  const listeners = new Set<() => void>()

  // Un 401 en mitad de la sesión (cookie caducada) → se avisa a quien escuche.
  setUnauthorizedHandler(() => listeners.forEach((listener) => listener()))

  return {
    async restoreSession() {
      try {
        return await http.get<User>('/auth/me')
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null // no hay sesión
        throw err
      }
    },

    login: (credentials) => http.post<User>('/auth/login', credentials),
    register: (data) => http.post<User>('/auth/register', data),

    async logout() {
      await http.post<void>('/auth/logout', {})
    },

    getAuthHeaders: () => ({}), // nada: la cookie la pone el navegador

    onSessionExpired(listener) {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
  }
}
