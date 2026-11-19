import type { Product } from '../services/types'
import { CATEGORY_EMOJI, CATEGORY_LABELS, formatPrice } from '../utils/format'
import { StockBadge } from './StockBadge'

interface Props {
  product: Product
  onOpen: () => void
}

export function ProductCard({ product, onOpen }: Props) {
  return (
    <article className="card product" onClick={onOpen}>
      <div className="product-image" aria-hidden>
        {CATEGORY_EMOJI[product.category]}
      </div>
      <h3>{product.name}</h3>
      <p className="muted">{CATEGORY_LABELS[product.category]}</p>
      <div className="product-footer">
        <strong>{formatPrice(product.price_cents)}</strong>
        <StockBadge stock={product.stock} />
      </div>
    </article>
  )
}
