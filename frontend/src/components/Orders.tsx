import { useApi } from '../hooks/useApi'
import { orderService } from '../services/orderService'
import { STATUS_LABELS, formatDate, formatPrice } from '../utils/format'

interface Props {
  // Cambia cada vez que algo modifica los pedidos (p. ej. el agente): fuerza a recargar.
  refreshKey: number
}

export function Orders({ refreshKey }: Props) {
  const { data: orders, error, loading } = useApi(orderService.list, [refreshKey])

  if (loading && !orders) return <p className="muted">Cargando pedidos…</p>
  if (error) return <p className="error">{error}</p>
  if (!orders?.length) return <p className="muted">Todavía no tienes pedidos.</p>

  return (
    <section className="orders">
      {orders.map((order) => (
        <article key={order.id} className="card order">
          <header>
            <h3>Pedido #{order.id}</h3>
            <span className={`status ${order.status}`}>{STATUS_LABELS[order.status]}</span>
          </header>
          <p className="muted small">
            {formatDate(order.created_at)} · {order.shipping_address}
          </p>
          <ul>
            {order.items.map((item) => (
              <li key={item.product_id}>
                {item.quantity} × {item.product_name}
                <span className="num">{formatPrice(item.unit_price_cents * item.quantity)}</span>
              </li>
            ))}
          </ul>
          <p className="total">
            Total <strong>{formatPrice(order.total_cents)}</strong>
          </p>
        </article>
      ))}
      <p className="muted small">¿Quieres cancelar un pedido o cambiar la dirección? Pídeselo al asistente 💬</p>
    </section>
  )
}
