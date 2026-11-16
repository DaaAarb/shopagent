import { createContext } from 'react'
import type { Product } from '../services/types'

export interface CartLine {
  product: Product
  quantity: number
}

export interface CartState {
  lines: CartLine[]
  count: number
  totalCents: number
  add(product: Product): void
  setQuantity(productId: number, quantity: number): void
  quantityOf(productId: number): number
  clear(): void
}

export const CartContext = createContext<CartState | null>(null)
