import type { ReactNode } from 'react'

/** Saltos de línea y **negrita** en las respuestas del modelo.
 *  Genera elementos React, nunca HTML: el texto del modelo no puede inyectar scripts. */
export function renderRichText(text: string): ReactNode {
  return text.split('\n').map((line, i) => (
    <p key={i}>
      {line.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
        part.startsWith('**') && part.endsWith('**') ? <strong key={j}>{part.slice(2, -2)}</strong> : part,
      )}
    </p>
  ))
}
