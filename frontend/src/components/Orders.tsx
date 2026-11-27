import { useApi } from '../hooks/useApi'
import { orderService } from '../services/orderService'
import { STATUS_LABELS, formatDate, formatPrice } from '../utils/format'

interface Props {
  // Cambia cuando algo externo (el agente) modifica los pedidos y fuerza la recarga.
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
          <div className="order-meta muted small">
            <span>{formatDate(order.created_at)}</span>
            <span>{order.shipping_address}</span>
          </div>
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
      <p className="muted small">¿Quieres cancelar un pedido o cambiar la dirección? Pídeselo al asistente.</p>
    </section>
  )
}
