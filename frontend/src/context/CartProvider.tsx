import { useMemo, useState, type ReactNode } from 'react'
import type { Product } from '../services/types'
import { CartContext, type CartLine, type CartState } from './CartContext'

/** Carrito en memoria; se reinicia al cambiar de usuario (ver App.tsx). */
export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([])

  const value = useMemo<CartState>(() => {
    const add = (product: Product) =>
      setLines((prev) =>
        prev.some((l) => l.product.id === product.id)
          ? prev.map((l) => (l.product.id === product.id ? { ...l, quantity: l.quantity + 1 } : l))
          : [...prev, { product, quantity: 1 }],
      )

    const setQuantity = (productId: number, quantity: number) =>
      setLines((prev) =>
        quantity <= 0
          ? prev.filter((l) => l.product.id !== productId)
          : prev.map((l) => (l.product.id === productId ? { ...l, quantity } : l)),
      )

    return {
      lines,
      count: lines.reduce((sum, l) => sum + l.quantity, 0),
      // Orientativo: el total real lo calcula el backend.
      totalCents: lines.reduce((sum, l) => sum + l.product.price_cents * l.quantity, 0),
      add,
      setQuantity,
      quantityOf: (productId) => lines.find((l) => l.product.id === productId)?.quantity ?? 0,
      clear: () => setLines([]),
    }
  }, [lines])

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
