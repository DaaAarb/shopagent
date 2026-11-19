import type { Product } from '../services/types'
import { CATEGORY_EMOJI, CATEGORY_LABELS, formatPrice } from '../utils/format'
import { StockBadge } from './StockBadge'

interface Props {
  product: Product
  onOpen: () => void
}

export function ProductCard({ product, onOpen }: Props) {
  return (
    <article className="card product">
      <div className="product-image" aria-hidden>
        {CATEGORY_EMOJI[product.category]}
      </div>
      <h3>
        {/* Un botón real: se alcanza con Tab y se abre con Enter o Espacio. Su ::after
            (ver App.css) cubre toda la tarjeta, así que con el ratón se puede pulsar en cualquier punto. */}
        <button type="button" className="product-open" onClick={onOpen}>
          {product.name}
        </button>
      </h3>
      <p className="muted">{CATEGORY_LABELS[product.category]}</p>
      <div className="product-footer">
        <strong>{formatPrice(product.price_cents)}</strong>
        <StockBadge stock={product.stock} />
      </div>
    </article>
  )
}
