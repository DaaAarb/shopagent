# Diario de desarrollo

Entradas en orden inverso (la más reciente arriba).

## 2026-11-11
- **Hecho:** arranque del proyecto (8-11 nov). Esqueleto del repo y README vivo; modelo de datos (`User`, `Product`, `Order`, `OrderItem`, `Ticket`); capa de servicios con reglas de negocio y permisos (`OrderService`, `TicketService`, `UserService`); API REST de pedidos, tickets y usuarios con autenticación simulada (`X-User-Id`) y errores traducidos a HTTP en un único sitio; repo separado en `backend/` y `frontend/`. 51 tests, 100 % de cobertura en `services/`. Alcance ampliado (catálogo, stock, *checkout*, React con visor 3D) y plan comprimido hasta el 17-nov. ADRs 0001-0003.
- **Aprendido:** el dinero se guarda en céntimos como entero porque los enteros suman de forma exacta y los `float`/`double` no. La inyección de dependencias consiste en que una función pide los valores que necesita y quien la llama decide cuáles darle (la BD real en la API, una en memoria en los tests). Las *fixtures* de pytest se inyectan por coincidencia de nombre: si un test tiene un parámetro llamado igual que una fixture, pytest la ejecuta y le pasa el resultado. El `@` es un decorador; en FastAPI registra la función de debajo como la que atiende un método HTTP y una ruta.
- **Problema resuelto:** los modelos de tabla de SQLModel no validan los datos (un `Field(ge=0)` no impedía un total negativo): la validación se movió a los esquemas de entrada y a los servicios. SQLite ignora las claves foráneas por defecto: se activan en cada conexión para que se comporte como PostgreSQL.
- **Siguiente paso:** día 11 del plan: máquina de estados, *checkout* con stock en una transacción, catálogo (`GET /products`), endpoints de demo, `seed.py` con el catálogo de Loba Toys; cerrar la fase 1 con `v0.1`.
