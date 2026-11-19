import { useEffect, useRef } from 'react'
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
  const dialogRef = useRef<HTMLDivElement>(null)
  // Siempre la última versión de onClose, sin tener que volver a montar el efecto de abajo.
  const closeRef = useRef(onClose)
  useEffect(() => {
    closeRef.current = onClose
  })

  // Accesibilidad del diálogo: al abrir, el foco entra en él; Escape lo cierra; Tab no se
  // sale hacia la página de detrás; y al cerrar el foco vuelve a donde estaba.
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
      {/* stopPropagation: un clic dentro del modal no debe cerrarlo. */}
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
