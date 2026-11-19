import { http } from './httpClient'
import type { Order, OrderCreate } from './types'

// Ninguna función recibe el usuario: lo identifica la cabecera de autenticación,
// igual que en el backend (el cliente no puede pedir pedidos "de otro").
export const orderService = {
  list: () => http.get<Order[]>('/orders'),
  create: (data: OrderCreate) => http.post<Order>('/orders', data),
}
