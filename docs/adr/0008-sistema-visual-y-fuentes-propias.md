# 0008 · Sistema visual con variables CSS y fuentes servidas desde el proyecto

- **Estado:** aceptada
- **Fecha:** 2026-11-19

## Contexto
La primera versión de la interfaz tenía los colores repartidos por varios archivos CSS, usaba las fuentes del sistema y mostraba un emoji como imagen de cada producto. Además tenía problemas de accesibilidad: ningún control mostraba el foco, las tarjetas de producto solo se podían abrir con el ratón, el modal no se cerraba con Escape y varias insignias y bordes de campos no llegaban al contraste mínimo. Se quería una identidad visual reconocible sin tocar la estructura, las rutas ni la lógica.

## Decisión
- **Todo el diseño sale de variables en `:root`** (`index.css`): colores, fuentes, radios y sombras. El resto del CSS solo usa `var(--…)`, así que cambiar de aspecto es cambiar ese bloque.
- **Estilo "pegatina":** papel crema y tinta casi negra; el rosa marca lo que actúa (comprar, precios) y el lima lo que señala (etiquetas, contadores). Las tarjetas llevan un borde blanco recortado y una sombra dura desplazada, sin desenfoque.
- **Fuentes propias:** Bowlby One SC (titulares y precios) y Sofia Sans (texto) con `@fontsource`, empaquetadas con el frontend (licencia OFL-1.1). No hay peticiones a Google.
- **Imagen de producto:** mientras no haya fotos, cada producto es un bloque de color por categoría con su nombre, sin emoji ni dibujos. Las fotos reales ocuparán ese mismo hueco.
- **La accesibilidad forma parte del sistema:** `:focus-visible` en todos los controles; la tarjeta de producto es un botón real (Tab, Enter y Espacio); el modal se cierra con Escape, retiene el foco y lo devuelve al cerrar; texto con contraste de 4,5:1 o más (medido); los mensajes del chat se anuncian a lectores de pantalla; y `prefers-reduced-motion` desactiva las animaciones.

## Alternativas
- **Google Fonts desde su CDN:** es lo más sencillo, pero cada visita envía la IP del visitante a un tercero (delicado con el RGPD) y añade una dependencia externa en tiempo de ejecución.
- **Una biblioteca de componentes (MUI, shadcn, Tailwind):** más rápido de arrancar, pero con menos control del aspecto y más dependencias para un frontend pequeño.
- **Mantener los emoji:** se ven distinto en cada sistema y no se pueden diseñar ni dar nombre accesible.

## Consecuencias
- El aspecto es coherente y un cambio de tema es barato. Los colores de estado (stock, pedidos) son parte del sistema y se revisan con él.
- Dos dependencias nuevas (`@fontsource/bowlby-one-sc`, `@fontsource/sofia-sans`). El empaquetado incluye varios subconjuntos de caracteres; el navegador solo descarga los que usa la página. Si el peso importara, se podrían limitar al subconjunto latino.
- Cuando haya fotos de producto habrá que volver a comprobar el contraste de las etiquetas que se coloquen sobre ellas.
- No hay tests automáticos del frontend: la accesibilidad se verificó a mano con el teclado y con un análisis de estilos. Queda como mejora añadir pruebas.
