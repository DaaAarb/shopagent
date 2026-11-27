import type { DogSize, OrderStatus, ProductCategory } from '../services/types'

// Los importes llegan en céntimos.
const euros = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })
export const formatPrice = (cents: number) => euros.format(cents / 100)

const dates = new Intl.DateTimeFormat('es-ES', { dateStyle: 'medium' })
export const formatDate = (iso: string) => dates.format(new Date(iso))

// Record exhaustivo: una categoría nueva obliga a añadir su etiqueta.
export const CATEGORY_LABELS: Record<ProductCategory, string> = {
  balls: 'Pelotas',
  chew: 'Mordedores',
  rope: 'Cuerdas',
  plush: 'Peluches',
  interactive: 'Interactivos',
}

export const DOG_SIZE_LABELS: Record<DogSize, string> = {
  small: 'Perros pequeños',
  medium: 'Perros medianos',
  large: 'Perros grandes',
  all: 'Todos los tamaños',
}

export const STATUS_LABELS: Record<OrderStatus, string> = {
  pending: 'Pendiente de pago',
  paid: 'Pagado',
  shipped: 'Enviado',
  delivered: 'Entregado',
  cancelled: 'Cancelado',
}
