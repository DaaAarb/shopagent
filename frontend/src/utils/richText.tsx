import type { ReactNode } from 'react'

/** Formato mínimo de las respuestas del modelo: saltos de línea y **negrita**.
 *
 *  Se construyen elementos React, no HTML en bruto: el texto del modelo nunca se
 *  interpreta como HTML, así que una respuesta manipulada no puede inyectar scripts (XSS). */
export function renderRichText(text: string): ReactNode {
  return text.split('\n').map((line, i) => (
    <p key={i}>
      {line.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
        part.startsWith('**') && part.endsWith('**') ? <strong key={j}>{part.slice(2, -2)}</strong> : part,
      )}
    </p>
  ))
}
