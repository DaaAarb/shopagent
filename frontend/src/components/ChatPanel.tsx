import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useAuth } from '../hooks/useAuth'
import { chatService } from '../services/chatService'
import type { PendingAction } from '../services/types'
import { renderRichText } from '../utils/richText'

interface ChatMessage {
  role: 'user' | 'assistant' | 'error'
  text: string
}

interface Props {
  // Se llama cuando una acción confirmada cambia datos (para refrescar "Mis pedidos").
  onDataChanged: () => void
}

const SUGGESTIONS = ['¿Cómo va mi último pedido?', 'Quiero cancelar un pedido', 'Cambia la dirección de un pedido']

export function ChatPanel({ onDataChanged }: Props) {
  const { user } = useAuth()
  const firstName = user?.name.split(' ')[0] ?? ''
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pending, setPending] = useState<PendingAction | null>(null)
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  // Baja hasta el último mensaje cada vez que llega uno.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  const add = (message: ChatMessage) => setMessages((prev) => [...prev, message])

  async function send(text: string) {
    if (!text.trim() || busy) return
    add({ role: 'user', text })
    setInput('')
    setPending(null) // el backend descarta la acción pendiente con un mensaje nuevo
    setBusy(true)
    try {
      const reply = await chatService.send(text)
      add({ role: 'assistant', text: reply.reply })
      setPending(reply.pending_action)
    } catch (err) {
      add({ role: 'error', text: (err as Error).message })
    } finally {
      setBusy(false)
    }
  }

  async function resolve(approve: boolean) {
    if (!pending) return
    const action = pending
    setPending(null) // se ocultan los botones ya: evita el doble clic
    add({ role: 'user', text: approve ? 'Sí, confírmalo' : 'No, déjalo' })
    setBusy(true)
    try {
      const reply = await chatService.confirm(action.id, approve)
      add({ role: 'assistant', text: reply.reply })
      if (approve) onDataChanged()
    } catch (err) {
      add({ role: 'error', text: (err as Error).message })
    } finally {
      setBusy(false)
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void send(input)
  }

  return (
    <aside className="chat" aria-label="Asistente">
      <header>
        <strong>Asistente de Loba Toys</strong>
        <span className="muted small">Consulta, cancela o cambia tus pedidos</span>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome">
            <p>
              ¡Hola, {firstName}! 🐶 Puedo consultar tus pedidos, cancelarlos, cambiar la dirección o abrir una
              incidencia.
            </p>
            {SUGGESTIONS.map((s) => (
              <button key={s} className="chip" onClick={() => void send(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {renderRichText(m.text)}
          </div>
        ))}

        {pending && (
          <div className="confirm-box">
            <p>
              <strong>{pending.description}</strong>
            </p>
            <div className="row">
              <button className="primary" disabled={busy} onClick={() => void resolve(true)}>
                Confirmar
              </button>
              <button disabled={busy} onClick={() => void resolve(false)}>
                Cancelar
              </button>
            </div>
          </div>
        )}

        {busy && <div className="bubble assistant typing">Escribiendo…</div>}
        <div ref={endRef} />
      </div>

      <form onSubmit={submit}>
        <input
          value={input}
          maxLength={2000}
          placeholder="Escribe tu mensaje…"
          aria-label="Mensaje"
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <button className="primary" disabled={busy || !input.trim()}>
          Enviar
        </button>
      </form>
    </aside>
  )
}
