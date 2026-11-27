import type { Product } from '../services/types'
import { CATEGORY_LABELS, formatPrice } from '../utils/format'
import { StockBadge } from './StockBadge'

interface Props {
  product: Product
  onOpen: () => void
}

export function ProductCard({ product, onOpen }: Props) {
  return (
    <article className="card product">
      <div className={`product-image cat-${product.category}`} aria-hidden>
        {CATEGORY_LABELS[product.category]}
      </div>
      <h3>
        <button type="button" className="product-open" onClick={onOpen}>
          {product.name}
        </button>
      </h3>
      <div className="product-footer">
        <strong className="price">{formatPrice(product.price_cents)}</strong>
        <StockBadge stock={product.stock} />
      </div>
    </article>
  )
}
