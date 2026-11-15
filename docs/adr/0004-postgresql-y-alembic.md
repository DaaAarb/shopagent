# 0004 · PostgreSQL en todos los entornos y migraciones con Alembic

- **Estado:** aceptada (sustituye a la [0001](0001-sqlite-dev-postgresql-prod.md))
- **Fecha:** 2026-11-13

## Contexto
La [0001](0001-sqlite-dev-postgresql-prod.md) usaba SQLite en desarrollo y tests y PostgreSQL solo en producción. Las diferencias entre motores (claves foráneas, tipos `ENUM`, fechas con zona horaria, concurrencia) solo aparecerían al desplegar. Además, el esquema se creaba con `create_all` al arrancar la app, sin historial de cambios.

## Decisión
- **PostgreSQL 17** en desarrollo, tests y producción. En local se levanta con `docker compose up -d db`, que crea también la base `shopagent_test`.
- Driver **psycopg 3** (`postgresql+psycopg://...`); URLs en `DATABASE_URL` y `TEST_DATABASE_URL`.
- El esquema lo gestiona **Alembic** (`backend/migrations/`): `alembic upgrade head` crea o actualiza las tablas; la app ya no llama a `create_all`. `env.py` lee la URL de `app.config`, nunca de `alembic.ini`.
- Los tests aplican las migraciones al empezar y aíslan cada test en una transacción que se revierte al final (los `commit()` de los servicios se convierten en *savepoints*).
- Un test (`test_migrations.py`) equivale a `alembic check`: falla si un modelo cambia sin su migración.

## Alternativas
- **Mantener SQLite en dev/tests:** cero dependencias, pero el riesgo de diferencias entre motores sigue ahí.
- **`create_all` sin migraciones:** sencillo, pero no sabe modificar tablas existentes ni deja historial.
- **Testcontainers** (un PostgreSQL por ejecución de tests): más aislado, pero más lento y otra dependencia más.

## Consecuencias
- Desarrollo, tests y producción usan el mismo motor y el mismo esquema (el de las migraciones).
- Hace falta Docker para ejecutar la app y los tests en local.
- Cada cambio de modelo exige generar y revisar una migración (`alembic revision --autogenerate`).
