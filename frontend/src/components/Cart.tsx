import { useState, type FormEvent } from 'react'
import { useCart } from '../hooks/useCart'
import { orderService } from '../services/orderService'
import type { Order } from '../services/types'
import { formatPrice } from '../utils/format'

interface Props {
  onOrdered: (order: Order) => void
}

export function Cart({ onOrdered }: Props) {
  const cart = useCart()
  const [address, setAddress] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  if (cart.lines.length === 0) {
    return <p className="muted">El carrito está vacío. Echa un vistazo al catálogo 🐾</p>
  }

  async function checkout(event: FormEvent) {
    event.preventDefault() // evita que el formulario recargue la página
    setSending(true)
    setError(null)
    try {
      const order = await orderService.create({
        items: cart.lines.map((l) => ({ product_id: l.product.id, quantity: l.quantity })),
        shipping_address: address,
      })
      cart.clear()
      onOrdered(order)
    } catch (err) {
      // P. ej. 409 si otro cliente se llevó el stock mientras tanto.
      setError((err as Error).message)
      setSending(false)
    }
  }

  return (
    <section className="cart">
      <table>
        <tbody>
          {cart.lines.map(({ product, quantity }) => (
            <tr key={product.id}>
              <td>{product.name}</td>
              <td>
                <input
                  type="number"
                  min={0}
                  max={product.stock}
                  value={quantity}
                  aria-label={`Unidades de ${product.name}`}
                  onChange={(e) => cart.setQuantity(product.id, Number(e.target.value))}
                />
              </td>
              <td className="num">{formatPrice(product.price_cents * quantity)}</td>
              <td>
                <button className="link" onClick={() => cart.setQuantity(product.id, 0)}>
                  Quitar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={2}>Total</td>
            <td className="num">
              <strong>{formatPrice(cart.totalCents)}</strong>
            </td>
            <td />
          </tr>
        </tfoot>
      </table>

      <form onSubmit={checkout} className="checkout">
        <label>
          Dirección de envío
          <input
            required
            maxLength={200}
            value={address}
            placeholder="Calle, número, código postal y ciudad"
            onChange={(e) => setAddress(e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={sending}>
          {sending ? 'Enviando…' : 'Hacer pedido'}
        </button>
        <p className="muted small">Pago simulado: el pedido se crea como «pendiente de pago».</p>
      </form>
    </section>
  )
}
