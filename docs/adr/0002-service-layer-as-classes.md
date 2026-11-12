# 0002 · Capa de servicios como clases con la sesión inyectada

- **Estado:** aceptada
- **Fecha:** 2026-11-08

## Contexto
Las reglas de negocio y los permisos deben vivir en un único sitio que usen tanto la API como el agente. Había que elegir entre funciones sueltas o clases.

## Decisión
- Un servicio por agregado (`OrderService`, `TicketService`, `UserService`), con la **sesión de base de datos inyectada en el constructor**.
- Cada método recibe el `user_id` de quien pregunta y comprueba la propiedad del recurso.
- Las operaciones que modifican un pedido pasan primero por `get_order`, que hace esa comprobación.
- Los errores se expresan con **excepciones del dominio** (`OrderNotFound`, `InvalidOrderState`, …), sin saber nada de HTTP ni del LLM.

## Alternativas
- **Funciones sueltas:** más simples, pero dispersan las operaciones y dificultan añadir comportamiento común (decoradores, logging, transacciones).

## Consecuencias
- Organización clara y extensible; fácil de testear con una base en memoria.
- `api/` traduce las excepciones a HTTP en un único manejador; `agent/` las traducirá a mensajes para el modelo.
