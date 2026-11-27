"""Repositorio genérico con el acceso a datos común a todos los modelos.

Los repositorios nunca hacen commit: la transacción la confirma la UnitOfWork
desde services/, porque una operación de negocio puede tocar varios repositorios.
"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.sql import ColumnElement
from sqlmodel import Session, SQLModel, select


class Repository[T: SQLModel]:
    # Lo fija cada subclase: el parámetro de tipo T no existe en tiempo de ejecución.
    model: type[T]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: int) -> T | None:
        return self.session.get(self.model, entity_id)

    def find(
        self, *conditions: ColumnElement[bool], order_by: Sequence[Any] = ()
    ) -> list[T]:
        statement = select(self.model).where(*conditions).order_by(*order_by)
        return list(self.session.exec(statement).all())

    def add(self, entity: T) -> T:
        """Añade la entidad a la transacción; `flush` le asigna el `id` sin confirmar."""
        self.session.add(entity)
        self.session.flush()
        return entity
