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
      {/* Hueco de la imagen: sin fotos aún, un relleno de color por categoría con su nombre. */}
      <div className={`product-image cat-${product.category}`} aria-hidden>
        {CATEGORY_LABELS[product.category]}
      </div>
      <h3>
        {/* Un botón real: se alcanza con Tab y se abre con Enter o Espacio. Su ::after
            (ver App.css) cubre toda la tarjeta, así que con el ratón se puede pulsar en cualquier punto. */}
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
