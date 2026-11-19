import { useContext } from 'react'
import { CartContext, type CartState } from '../context/CartContext'

export function useCart(): CartState {
  const cart = useContext(CartContext)
  if (!cart) throw new Error('useCart debe usarse dentro de <CartProvider>.')
  return cart
}
