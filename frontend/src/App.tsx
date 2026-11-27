import { useState } from 'react'
import './App.css'
import { Cart } from './components/Cart'
import { Catalog } from './components/Catalog'
import { ChatPanel } from './components/ChatPanel'
import { Header, type View } from './components/Header'
import { LoginPage } from './components/LoginPage'
import { Orders } from './components/Orders'
import { CartProvider } from './context/CartProvider'
import { useAuth } from './hooks/useAuth'
import type { Order, Product } from './services/types'

/** Decide qué se ve según la sesión: cargando, login o la tienda. */
export default function App() {
  const { user, restoring } = useAuth()

  if (restoring) return <p className="muted page">Cargando…</p>
  if (!user) return <LoginPage />

  // key={user.id}: al cambiar de usuario se remonta la tienda y no queda estado del anterior.
  return (
    <CartProvider key={user.id}>
      <Shop />
    </CartProvider>
  )
}

function Shop() {
  const [view, setView] = useState<View>('catalog')
  const [ordersVersion, setOrdersVersion] = useState(0)
  const [notice, setNotice] = useState<string | null>(null)
  const refreshOrders = () => setOrdersVersion((v) => v + 1)

  function ordered(order: Order) {
    refreshOrders()
    setNotice(`Pedido #${order.id} creado`)
    setView('orders')
  }

  return (
    <div className="layout">
      <Header view={view} onNavigate={setView} />

      {notice && (
        <div className="notice" role="status" onClick={() => setNotice(null)}>
          {notice}
        </div>
      )}

      <main>
        {view === 'catalog' && (
          <Catalog onAdded={(p: Product) => setNotice(`${p.name} añadido al carrito`)} />
        )}
        {view === 'cart' && <Cart onOrdered={ordered} />}
        {view === 'orders' && <Orders refreshKey={ordersVersion} />}
      </main>

      <ChatPanel onDataChanged={refreshOrders} />
    </div>
  )
}
