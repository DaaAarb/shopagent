import { useState, type FormEvent } from 'react'
import logo from '../assets/logo.svg'
import { useAuth } from '../hooks/useAuth'

type Mode = 'login' | 'register'

// Cuentas de prueba que crea backend/scripts/seed.py (datos ficticios).
const DEMO_PASSWORD = 'loba1234'
const DEMO_ACCOUNTS = [
  { name: 'Lucía', email: 'lucia@example.com' },
  { name: 'Marcos', email: 'marcos@example.com' },
  { name: 'Sofía', email: 'sofia@example.com' },
]

/** Pantalla de acceso. Solo habla con useAuth(): no sabe cómo se guarda la sesión. */
export function LoginPage() {
  const { login, register, expired } = useAuth()
  const [mode, setMode] = useState<Mode>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSending(true)
    setError(null)
    try {
      if (mode === 'login') await login({ email, password })
      else await register({ name, email, password })
      // Si va bien, este componente desaparece (App pinta la tienda): no se toca su estado.
    } catch (err) {
      setError((err as Error).message)
      setSending(false)
    }
  }

  function switchMode() {
    setMode(mode === 'login' ? 'register' : 'login')
    setError(null)
  }

  function fillDemoAccount(demoEmail: string) {
    setEmail(demoEmail)
    setPassword(DEMO_PASSWORD)
    setError(null)
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <img src={logo} alt="" className="auth-logo" />
        <h1>Loba Toys</h1>
        <p className="muted">{mode === 'login' ? 'Inicia sesión para ver tus pedidos' : 'Crea tu cuenta'}</p>

        {expired && mode === 'login' && (
          <p className="warning small">Tu sesión ha caducado. Vuelve a iniciar sesión.</p>
        )}

        <form onSubmit={submit} className="auth-form">
          {mode === 'register' && (
            <label>
              Nombre
              <input required maxLength={100} value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" />
            </label>
          )}
          <label>
            Email
            <input
              required
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
          <label>
            Contraseña
            <input
              required
              type="password"
              // Mismo mínimo que el backend (que es quien de verdad lo comprueba).
              minLength={mode === 'register' ? 8 : undefined}
              maxLength={128}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </label>
          {mode === 'register' && <p className="muted small">Mínimo 8 caracteres.</p>}
          {error && <p className="error">{error}</p>}
          <button className="primary" disabled={sending}>
            {sending ? 'Un momento…' : mode === 'login' ? 'Entrar' : 'Crear cuenta'}
          </button>
        </form>

        <button className="link" onClick={switchMode}>
          {mode === 'login' ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
        </button>

        {mode === 'login' && (
          <div className="demo-users">
            <p className="muted small">
              Demo · cuentas de prueba (contraseña <code>{DEMO_PASSWORD}</code>):
            </p>
            {DEMO_ACCOUNTS.map((account) => (
              <button key={account.email} type="button" className="chip" onClick={() => fillDemoAccount(account.email)}>
                {account.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
