import { useState, type FormEvent } from 'react'
import logo from '../assets/logo.svg'
import { useApi } from '../hooks/useApi'
import { useAuth } from '../hooks/useAuth'
import type { User } from '../services/types'

type Mode = 'login' | 'register'

/** Pantalla de acceso. Solo habla con useAuth(): no sabe si el login es de demo o real. */
export function LoginPage() {
  const { login, register, listDemoUsers } = useAuth()
  const [mode, setMode] = useState<Mode>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  async function run(action: () => Promise<void>) {
    setSending(true)
    setError(null)
    try {
      await action()
    } catch (err) {
      setError((err as Error).message)
      setSending(false) // si va bien, este componente desaparece: no se toca su estado
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void run(() => (mode === 'login' ? login({ email, password }) : register({ name, email, password })))
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <img src={logo} alt="" className="auth-logo" />
        <h1>Loba Toys</h1>
        <p className="muted">{mode === 'login' ? 'Inicia sesión para ver tus pedidos' : 'Crea tu cuenta'}</p>

        <form onSubmit={submit} className="auth-form">
          {mode === 'register' && (
            <label>
              Nombre
              <input required value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" />
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="primary" disabled={sending}>
            {mode === 'login' ? 'Entrar' : 'Crear cuenta'}
          </button>
        </form>

        <button className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
        </button>

        {/* Solo aparece si la implementación de auth ofrece usuarios de demo. */}
        {listDemoUsers && mode === 'login' && (
          <DemoUsers
            load={listDemoUsers}
            disabled={sending}
            onPick={(user) => void run(() => login({ email: user.email, password: 'demo' }))}
          />
        )}
      </div>
    </div>
  )
}

interface DemoUsersProps {
  load: () => Promise<User[]>
  disabled: boolean
  onPick: (user: User) => void
}

function DemoUsers({ load, disabled, onPick }: DemoUsersProps) {
  const { data: users, error } = useApi(load)

  return (
    <div className="demo-users">
      <p className="muted small">Demo · entra con un cliente de prueba (sin contraseña real):</p>
      {error && <p className="error small">{error}</p>}
      {users?.map((user) => (
        <button key={user.id} className="chip" disabled={disabled} onClick={() => onPick(user)}>
          {user.name}
        </button>
      ))}
    </div>
  )
}
