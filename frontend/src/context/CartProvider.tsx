import { useMemo, useState, type ReactNode } from 'react'
import type { Product } from '../services/types'
import { CartContext, type CartLine, type CartState } from './CartContext'

/** Carrito en memoria del navegador. Se monta por usuario (ver App.tsx):
 *  al cambiar de sesión empieza vacío. */
export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([])

  const value = useMemo<CartState>(() => {
    // El estado se actualiza siempre creando un array NUEVO, nunca modificando el actual:
    // React compara referencias para saber si tiene que volver a pintar.
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
      // Orientativo: el total definitivo lo calcula el backend con los precios de la BD.
      totalCents: lines.reduce((sum, l) => sum + l.product.price_cents * l.quantity, 0),
      add,
      setQuantity,
      quantityOf: (productId) => lines.find((l) => l.product.id === productId)?.quantity ?? 0,
      clear: () => setLines([]),
    }
  }, [lines])

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
