// Cliente HTTP: el único sitio que llama a fetch.
//
// No sabe nada de autenticación. Quien la gestione le "inyecta" desde fuera:
// - `setAuthHeadersProvider`: cabeceras extra por petición (hoy ninguna: la sesión
//   va en una cookie que el navegador envía solo; con tokens sería `Authorization`);
// - `setUnauthorizedHandler`: qué hacer si el backend responde 401 (sesión caducada).

const BASE_URL = '/api' // Vite (y en producción el servidor web) lo reenvía al backend

/** Error HTTP con el mensaje `detail` que devuelve el backend (api/errors.py). */
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
    // Un 401 fuera de /auth/* significa que la sesión ha caducado. (En /auth/login es
    // "contraseña incorrecta" y en /auth/me "no hay sesión": eso lo trata quien llama).
    if (response.status === 401 && !path.startsWith('/auth/')) onUnauthorized()
    throw new ApiError(response.status, await errorMessage(response))
  }
  if (response.status === 204) return undefined as T // sin cuerpo (p. ej. logout)
  return (await response.json()) as T
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    // FastAPI devuelve `detail` como texto (errores propios) o como lista (422 de Pydantic).
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) return 'Revisa los datos introducidos.'
  } catch {
    // La respuesta no era JSON.
  }
  return `Error ${response.status}`
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}
