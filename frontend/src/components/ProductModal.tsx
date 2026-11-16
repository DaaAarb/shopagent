import { useCart } from '../hooks/useCart'
import type { Product } from '../services/types'
import { CATEGORY_EMOJI, DOG_SIZE_LABELS, formatPrice } from '../utils/format'

interface Props {
  product: Product
  onClose: () => void
  onAdded: (product: Product) => void
}

export function ProductModal({ product, onClose, onAdded }: Props) {
  const cart = useCart()
  const inCart = cart.quantityOf(product.id)
  // No se deja añadir más unidades de las que hay: el backend lo rechazaría igualmente (409).
  const canAdd = inCart < product.stock

  function add() {
    cart.add(product)
    onAdded(product)
  }

  return (
    <div className="backdrop" onClick={onClose}>
      {/* stopPropagation: un clic dentro del modal no debe cerrarlo. */}
      <div className="modal" role="dialog" aria-label={product.name} onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
        <div className="product-image large" aria-hidden>
          {CATEGORY_EMOJI[product.category]}
        </div>
        <h2>{product.name}</h2>
        <p>{product.description}</p>
        <ul className="specs">
          <li>
            <span className="muted">Material</span> {product.material}
          </li>
          <li>
            <span className="muted">Recomendado para</span> {DOG_SIZE_LABELS[product.dog_size]}
          </li>
          <li>
            <span className="muted">Disponibles</span> {product.stock}
          </li>
        </ul>
        <div className="product-footer">
          <strong className="price">{formatPrice(product.price_cents)}</strong>
          <button className="primary" disabled={!canAdd} onClick={add}>
            {product.stock === 0 ? 'Sin stock' : canAdd ? 'Añadir al carrito' : 'No quedan más'}
          </button>
        </div>
        {inCart > 0 && <p className="muted">Tienes {inCart} en el carrito.</p>}
      </div>
    </div>
  )
}
