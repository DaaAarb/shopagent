import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { productService } from '../services/productService'
import type { Product, ProductCategory } from '../services/types'
import { CATEGORY_LABELS } from '../utils/format'
import { ProductCard } from './ProductCard'
import { ProductModal } from './ProductModal'

const CATEGORIES = Object.keys(CATEGORY_LABELS) as ProductCategory[]

interface Props {
  onAdded: (product: Product) => void
}

export function Catalog({ onAdded }: Props) {
  // Catálogo pequeño (8 productos): se carga entero y se filtra en el cliente.
  const { data: products, error, loading } = useApi(productService.list)
  const [category, setCategory] = useState<ProductCategory | null>(null)
  const [selected, setSelected] = useState<Product | null>(null)

  if (loading) return <p className="muted">Cargando catálogo…</p>
  if (error) return <p className="error">{error}</p>

  const visible = (products ?? []).filter((p) => category === null || p.category === category)

  return (
    <section>
      <div className="chips" role="group" aria-label="Filtrar por categoría">
        <button className={category === null ? 'chip active' : 'chip'} onClick={() => setCategory(null)}>
          Todo
        </button>
        {CATEGORIES.map((c) => (
          <button key={c} className={category === c ? 'chip active' : 'chip'} onClick={() => setCategory(c)}>
            {CATEGORY_LABELS[c]}
          </button>
        ))}
      </div>

      <div className="grid">
        {visible.map((product) => (
          <ProductCard key={product.id} product={product} onOpen={() => setSelected(product)} />
        ))}
      </div>

      {selected && <ProductModal product={selected} onClose={() => setSelected(null)} onAdded={onAdded} />}
    </section>
  )
}
