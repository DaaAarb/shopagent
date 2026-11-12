# 0001 · SQLite en desarrollo, PostgreSQL en producción

- **Estado:** aceptada
- **Fecha:** 2026-11-08

## Contexto
El proyecto necesita una base de datos relacional. En desarrollo y en los tests prima la rapidez y no depender de servicios externos; en producción, la concurrencia y la fiabilidad.

## Decisión
- **SQLite** en desarrollo y en los tests (en memoria, una base nueva por test).
- **PostgreSQL** en producción.
- El cambio es solo de configuración: `DATABASE_URL` en `.env`, leída con pydantic-settings. El código usa SQLModel (SQLAlchemy), que abstrae el motor.
- Las claves foráneas se activan en SQLite (`PRAGMA foreign_keys=ON`) para que se comporte como PostgreSQL.

## Alternativas
- **PostgreSQL desde el principio** (con Docker): entorno idéntico a producción, pero más fricción al empezar y tests más lentos.
- **Solo SQLite:** no aguanta bien escrituras concurrentes en un despliegue real.

## Consecuencias
- Clonar, instalar y ejecutar sin levantar ningún servidor.
- Riesgo de diferencias entre motores: se mitiga activando claves foráneas y probando contra PostgreSQL en la CI.
