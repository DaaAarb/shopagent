import { useEffect, useRef } from 'react'
import { useCart } from '../hooks/useCart'
import type { Product } from '../services/types'
import { CATEGORY_LABELS, DOG_SIZE_LABELS, formatPrice } from '../utils/format'

interface Props {
  product: Product
  onClose: () => void
  onAdded: (product: Product) => void
}

export function ProductModal({ product, onClose, onAdded }: Props) {
  const cart = useCart()
  const inCart = cart.quantityOf(product.id)
  const canAdd = inCart < product.stock
  const dialogRef = useRef<HTMLDivElement>(null)
  // Ref a la última onClose para no volver a montar el efecto del diálogo.
  const closeRef = useRef(onClose)
  useEffect(() => {
    closeRef.current = onClose
  })

  // Diálogo accesible: foco inicial, Escape, foco atrapado y foco restaurado al cerrar.
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null
    dialogRef.current?.focus()

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        closeRef.current()
        return
      }
      if (event.key !== 'Tab') return
      const focusable = dialogRef.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input, select, a[href]')
      if (!focusable || focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      const active = document.activeElement
      if (event.shiftKey && (active === first || active === dialogRef.current)) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && active === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      previous?.focus()
    }
  }, [])

  function add() {
    cart.add(product)
    onAdded(product)
  }

  return (
    <div className="backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={product.name}
        tabIndex={-1}
        ref={dialogRef}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="close" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
        <div className={`product-image large cat-${product.category}`} aria-hidden>
          {CATEGORY_LABELS[product.category]}
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
