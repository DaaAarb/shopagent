# 0006 · Diseño del agente: interfaz de LLM, confirmación en el backend e historial en Redis

- **Estado:** aceptada
- **Fecha:** 2026-11-16

## Contexto
El agente de atención al cliente ejecuta acciones reales sobre la base de datos (cancelar pedidos, cambiar direcciones). Un LLM no es fiable: puede equivocarse de argumentos, inventar datos o ser manipulado por el texto del cliente (*prompt injection*). Además el proyecto debe funcionar sin coste, poder cambiar de proveedor y probarse sin llamar a ningún modelo real.

## Decisión
- **Interfaz propia de LLM** (`agent/llm.py`): tipos de mensaje neutros (`Message`, `ToolCall`, `ToolResult`) y un `Protocol` `LLMClient` con un único método `generate`. **El adaptador de Gemini** (`agent/gemini.py`) es el único módulo que importa el SDK de Google y traduce en ambos sentidos. Se usa Gemini por su capa gratuita; el modelo se elige con `LLM_MODEL`.
- **El bucle de *tool use* es nuestro**, no el automático del SDK: como mucho 5 vueltas por turno, y cada llamada a herramienta se valida con Pydantic antes de ejecutarse. Un error de validación vuelve al modelo para que corrija.
- **El `user_id` nunca es un argumento de las herramientas**: lo pone el backend a partir de la cabecera autenticada. Los permisos los aplican los servicios, igual que en la API.
- **Confirmación en el backend:** las herramientas destructivas no se ejecutan cuando el modelo las pide. El backend guarda una acción pendiente con un id aleatorio y devuelve al cliente una pregunta escrita por el backend (no por el modelo). Solo `POST /chat/confirm` con ese id la ejecuta. La acción se borra antes de ejecutarse, se vuelve a validar y el servicio vuelve a comprobar las reglas de negocio. Un mensaje nuevo la descarta, y solo puede haber una por turno.
- **Historial y acción pendiente en Redis**, por usuario, con caducidad de 24 h y un máximo de 30 mensajes. El recorte siempre empieza en un mensaje del cliente, para no dejar resultados de herramientas huérfanos.

## Alternativas
- **Usar el SDK de Gemini directamente en el agente:** menos código, pero ata todo el proyecto a un proveedor y obliga a simular el SDK en los tests.
- **Confirmación delegada al modelo** (que pregunte y, si el cliente dice "sí", llame a la herramienta): depende de que el modelo obedezca; un texto manipulado podría saltársela.
- **Historial en PostgreSQL o en memoria del proceso:** PostgreSQL sirve, pero el chat es efímero y Redis lo caduca solo; en memoria se pierde al reiniciar y no escala a varias instancias.

## Consecuencias
- La seguridad no depende del prompt: aunque el modelo desobedezca, no puede leer pedidos ajenos ni ejecutar nada destructivo sin el clic del cliente.
- Los tests del agente usan un LLM falso guionizado y un historial en memoria: son deterministas, rápidos y gratuitos.
- Cambiar de proveedor (por ejemplo, a Claude u OpenAI) es escribir otro adaptador, sin tocar el bucle ni las herramientas.
- Un servicio más que arrancar (Redis) y una dependencia externa (Gemini) que puede fallar o ir lenta: la API responde 503 sin exponer detalles.
