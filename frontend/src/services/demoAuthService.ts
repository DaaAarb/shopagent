// Implementación de DEMO del contrato AuthService.
//
// El backend aún no tiene login: "entrar" es identificarse como uno de los
// clientes de prueba, y cada petición lleva la cabecera simulada X-User-Id.
// La contraseña NO se comprueba (no hay credenciales en el backend).

import type { AuthService } from './authService'
import { ApiError, http } from './httpClient'
import type { User } from './types'

const SESSION_KEY = 'lobatoys.session'

// localStorage puede no estar disponible (modo privado, bloqueado…): nunca debe romper la app.
function readSession(): string | null {
  try {
    return localStorage.getItem(SESSION_KEY)
  } catch {
    return null
  }
}

function writeSession(value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(SESSION_KEY)
    else localStorage.setItem(SESSION_KEY, value)
  } catch {
    // Sin persistencia: la sesión dura lo que la pestaña.
  }
}

export function createDemoAuthService(): AuthService {
  // Clausura: esta variable solo es accesible desde las funciones de abajo.
  let currentUserId: number | null = null

  const listUsers = () => http.get<User[]>('/users')

  return {
    async restoreSession() {
      const saved = Number(readSession())
      if (!saved) return null
      const user = (await listUsers()).find((u) => u.id === saved) ?? null
      currentUserId = user?.id ?? null
      if (!user) writeSession(null) // ya no existe (p. ej. tras volver a ejecutar el seed)
      return user
    },

    async login({ email }) {
      const wanted = email.trim().toLowerCase()
      const user = (await listUsers()).find((u) => u.email.toLowerCase() === wanted)
      if (!user) throw new ApiError(401, 'No existe ningún cliente con ese email.')
      currentUserId = user.id
      writeSession(String(user.id))
      return user
    },

    async register() {
      throw new ApiError(501, 'El registro no está disponible en la demo. Entra con un cliente de prueba.')
    },

    logout() {
      currentUserId = null
      writeSession(null)
    },

    getAuthHeaders(): Record<string, string> {
      return currentUserId === null ? {} : { 'X-User-Id': String(currentUserId) }
    },

    listDemoUsers: listUsers,
  }
}
