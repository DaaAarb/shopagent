# 0005 · Repositorio genérico, unidad de trabajo y DTOs

- **Estado:** aceptada (sustituye en parte a la [0002](0002-service-layer-as-classes.md): los servicios ya no reciben la sesión, sino una unidad de trabajo)
- **Fecha:** 2026-11-13

## Contexto
Los servicios mezclaban dos responsabilidades: las reglas de negocio y la construcción de consultas a la base de datos. Además, cada servicio hacía su propio `commit`, lo que complica las operaciones que tocan varias tablas a la vez: cancelar un pedido cambia el pedido **y** repone el stock de sus productos, y el *checkout* hará lo mismo al revés. Por otro lado, la API y el agente necesitan los mismos mensajes estructurados, y el frontend los recibe como JSON.

## Decisión
- **Repositorio genérico** `Repository[T]` con las operaciones comunes (`get`, `find`, `add`), escrito una vez para cualquier modelo gracias a los genéricos de Python. Cada entidad tiene su repositorio (`OrderRepository(Repository[Order])`, …), que hereda lo común y añade solo sus consultas propias (`list_for_user`, …).
- **Los repositorios nunca hacen `commit`.** Solo preparan cambios (`flush` para obtener el `id`).
- **Unidad de trabajo** (`UnitOfWork`): agrupa los repositorios sobre una misma sesión y es la única que confirma. Usada con `with uow:`, deshace automáticamente lo pendiente si salta una excepción. Los servicios la reciben inyectada: `OrderService(uow)`.
- **DTOs** en `app/dtos/`, un archivo por entidad: los de entrada validan (`AddressUpdate`, `TicketCreate`) y los de salida deciden qué se expone (`OrderRead`, …). **Los servicios devuelven DTOs**: las entidades del ORM no salen de `services/`. La API, el agente y el frontend comparten este contrato.

Capas: `api/` y `agent/` → `services/` (reglas, permisos, transacciones) → `repositories/` (consultas) → `models/` → base de datos.

## Alternativas
- **Un repositorio por entidad sin clase base:** más simple de leer, pero repite el mismo código en cada uno.
- **Interfaz abstracta (`Protocol`) con implementación SQL y otra en memoria para tests:** más flexible, pero duplica el código; los tests ya usan una base de datos real y aislada.
- **Que cada repositorio haga `commit`:** rompe la atomicidad de las operaciones que tocan varias tablas.
- **Servicios que devuelven entidades:** obligan a la API y al agente a conocer el ORM y a convertir los datos con la sesión todavía abierta (carga perezosa de relaciones).

## Consecuencias
- Las transacciones de varias tablas (cancelar con reposición de stock, *checkout*) quedan explícitas y en un único punto.
- Añadir una entidad nueva cuesta una clase de pocas líneas.
- Las rutas quedan reducidas a traducir HTTP: reciben un DTO del servicio y lo devuelven tal cual.
- Una capa más que recorrer al leer el código; se compensa con responsabilidades más claras.
