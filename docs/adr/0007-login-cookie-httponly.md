# 0007 · Login con contraseña y sesión en cookie httpOnly

- **Estado:** aceptada (sustituye a la autenticación simulada con la cabecera `X-User-Id`)
- **Fecha:** 2026-11-17

## Contexto
Hasta ahora quien llamaba a la API decía quién era con la cabecera `X-User-Id`, y el backend se lo creía: con `curl -H "X-User-Id: 2"` cualquiera actuaba como otro cliente. Además, `GET /users` listaba públicamente los nombres y emails de todos los clientes. El resto del sistema ya recibía un `user_id` resuelto en un único punto (`get_current_user_id`), así que el cambio podía quedar acotado.

## Decisión
- **Contraseñas con hash argon2** (`pwdlib`), nunca en claro. La columna `password_hash` no aparece en ningún DTO de salida.
- **Sesión = JWT firmado** con `SECRET_KEY` (HS256, `PyJWT`): contiene `sub` (el id del usuario) y `exp` (caduca en 60 min). Al leerlo se fija el algoritmo, para rechazar tokens sin firma (`alg: none`).
- **El token viaja en una cookie `session` con `HttpOnly`, `SameSite=Lax` y `Secure` en producción.** El frontend nunca lo ve: sabe si hay sesión preguntando a `GET /auth/me`, y el logout lo hace el servidor (`POST /auth/logout`).
- **Endpoints:** `POST /auth/register` (inicia sesión directamente), `POST /auth/login`, `POST /auth/logout` y `GET /auth/me`. Se elimina `GET /users`.
- **No revelar quién está registrado:** el login responde lo mismo ("Email o contraseña incorrectos") si el email no existe o si la contraseña falla, y tarda lo mismo, porque se verifica contra un hash de relleno.
- **Emails en minúsculas** al registrarse y al entrar; la restricción `UNIQUE` de la base de datos resuelve dos registros simultáneos.
- En el frontend, `cookieAuthService.ts` cumple la interfaz `AuthService` y sustituye a la de demo cambiando una línea en `main.tsx`. Un 401 en mitad de la sesión devuelve al login con un aviso.

## Alternativas
- **Token en `localStorage` + cabecera `Authorization: Bearer`:** más simple y cómodo de probar con `curl`, pero cualquier script inyectado (XSS) puede leer el token y llevárselo.
- **Sesiones guardadas en el servidor (Redis):** permiten cerrar una sesión concreta al instante, pero añaden una consulta en cada petición. Con un JWT de 60 minutos es suficiente para este proyecto.
- **Mantener `X-User-Id`:** no es autenticación; solo valía mientras no había login.

## Consecuencias
- Un XSS ya no puede robar la sesión. Podría hacer peticiones mientras la pestaña está abierta, por eso las respuestas del modelo se pintan sin interpretar HTML.
- CSRF queda cubierto por `SameSite=Lax`, porque el navegador no envía la cookie en POST desde otras webs. Requiere servir frontend y API **desde el mismo origen**: en desarrollo lo hace el proxy de Vite (`/api`) y en producción lo hará el servidor web.
- Un token emitido no se puede revocar antes de que caduque (el logout borra la cookie del navegador, no invalida el token). Es aceptable con 60 minutos.
- `SECRET_KEY` pasa a ser obligatoria y secreta: sin ella no se puede iniciar sesión.
- Los tests generan un token válido con `as_user(user)`, así que los tests existentes no cambiaron. Las pruebas de autenticación están en `test_auth.py`.
- Queda pendiente limitar los intentos de login (fuerza bruta), que entra en el *rate limiting* de la fase 4.
