// Único punto que llama a fetch. La autenticación se configura desde fuera con
// setAuthHeadersProvider y setUnauthorizedHandler.

const BASE_URL = '/api' // proxy al backend (Vite en desarrollo, servidor web en producción)

/** Error HTTP con el `detail` devuelto por el backend. */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

type HeadersProvider = () => Record<string, string>

let authHeaders: HeadersProvider = () => ({})

export function setAuthHeadersProvider(provider: HeadersProvider): void {
  authHeaders = provider
}

let onUnauthorized: () => void = () => {}

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  for (const [name, value] of Object.entries(authHeaders())) headers.set(name, value)

  let response: Response
  try {
    response = await fetch(BASE_URL + path, { ...init, headers })
  } catch {
    throw new ApiError(0, 'No se puede conectar con el servidor.')
  }

  if (!response.ok) {
    // Fuera de /auth/*, un 401 significa sesión caducada.
    if (response.status === 401 && !path.startsWith('/auth/')) onUnauthorized()
    throw new ApiError(response.status, await errorMessage(response))
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    // `detail` es texto (errores propios) o una lista (422 de validación).
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) return 'Revisa los datos introducidos.'
  } catch {
    // Respuesta sin cuerpo JSON: se usa el mensaje genérico.
  }
  return `Error ${response.status}`
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}
