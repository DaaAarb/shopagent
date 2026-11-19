import logo from '../assets/logo.svg'
import { useAuth } from '../hooks/useAuth'
import { useCart } from '../hooks/useCart'

export type View = 'catalog' | 'cart' | 'orders'

interface Props {
  view: View
  onNavigate: (view: View) => void
}

const TABS: { view: View; label: string }[] = [
  { view: 'catalog', label: 'Catálogo' },
  { view: 'cart', label: 'Carrito' },
  { view: 'orders', label: 'Mis pedidos' },
]

export function Header({ view, onNavigate }: Props) {
  const { user, logout } = useAuth()
  const { count } = useCart()

  return (
    <header className="topbar">
      <h1 className="brand">
        <img src={logo} alt="" /> Loba Toys
      </h1>
      <nav>
        {TABS.map((tab) => (
          <button
            key={tab.view}
            className={view === tab.view ? 'tab active' : 'tab'}
            onClick={() => onNavigate(tab.view)}
          >
            {tab.label}
            {tab.view === 'cart' && count > 0 && <span className="count">{count}</span>}
          </button>
        ))}
      </nav>
      <div className="session">
        <span className="small">{user?.name}</span>
        <button className="link" onClick={() => void logout()}>
          Salir
        </button>
      </div>
    </header>
  )
}
