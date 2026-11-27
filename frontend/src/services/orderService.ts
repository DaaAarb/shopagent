import { http } from './httpClient'
import type { Order, OrderCreate } from './types'

// El usuario lo identifica la sesión, no un parámetro.
export const orderService = {
  list: () => http.get<Order[]>('/orders'),
  create: (data: OrderCreate) => http.post<Order>('/orders', data),
}
