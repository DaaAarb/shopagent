# 0003 · Frontend en React en lugar de Streamlit

- **Estado:** aceptada (sustituye la elección inicial de Streamlit)
- **Fecha:** 2026-11-10

## Contexto
La primera idea era una interfaz de chat en Streamlit. El alcance creció: catálogo, ficha de producto, carrito, pedidos, chat y un visor 3D de los juguetes.

## Decisión
- **React + Vite** para la interfaz.
- **React Three Fiber** (three.js) para el visor 3D, en un modal y con carga bajo demanda: tiene un papel secundario.
- El frontend solo habla con el backend por HTTP; el repo se separa en `backend/` y `frontend/`, cada uno con sus dependencias.

## Alternativas
- **Streamlit:** muy rápido para prototipos en Python, pero con poco control del diseño y sin soporte natural para 3D ni para una tienda con varias vistas.
- **Streamlit con three.js incrustado:** posible, pero aislado en un iframe y difícil de integrar con el resto.

## Consecuencias
- Interfaz más completa y estándar.
- Más trabajo y una segunda tecnología (Node/JavaScript) en el proyecto.
- En el despliegue, backend y frontend serán imágenes Docker separadas.
