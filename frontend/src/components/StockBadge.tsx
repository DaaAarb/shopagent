export function StockBadge({ stock }: { stock: number }) {
  if (stock === 0) return <span className="badge danger">Sin stock</span>
  if (stock <= 3) return <span className="badge warn">¡Quedan {stock}!</span>
  return <span className="badge ok">En stock</span>
}
