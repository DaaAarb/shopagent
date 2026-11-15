"""Repositorio genérico: el acceso a datos común a cualquier modelo, escrito una vez.

`Repository[T]` funciona para cualquier modelo de tabla (User, Product, Order…).
Cada repositorio concreto hereda de él, indica su modelo y añade solo las
consultas propias de su entidad.

Regla clave: un repositorio NUNCA hace commit. Solo prepara cambios en la sesión.
Quien decide cuándo se confirma la transacción es la UnitOfWork (desde services/),
porque una misma operación de negocio puede tocar varios repositorios.
"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.sql import ColumnElement
from sqlmodel import Session, SQLModel, select


class Repository[T: SQLModel]:
    """`[T: SQLModel]` = "T es cualquier clase que herede de SQLModel".

    El tipo concreto se fija al heredar: `class OrderRepository(Repository[Order])`.
    """

    # Cada subclase lo rellena (p. ej. `model = Order`). Se necesita en tiempo de
    # ejecución para construir las consultas: el `T` de los genéricos solo existe
    # para el comprobador de tipos, no al ejecutar.
    model: type[T]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: int) -> T | None:
        """Busca por clave primaria. None si no existe."""
        return self.session.get(self.model, entity_id)

    def find(
        self, *conditions: ColumnElement[bool], order_by: Sequence[Any] = ()
    ) -> list[T]:
        """Todos los que cumplan las condiciones, en el orden indicado."""
        statement = select(self.model).where(*conditions).order_by(*order_by)
        return list(self.session.exec(statement).all())

    def add(self, entity: T) -> T:
        """Añade a la transacción en curso, sin confirmarla.

        `flush` envía el INSERT a la base de datos para que se asigne el `id`,
        pero si luego hay rollback, el INSERT se deshace.
        """
        self.session.add(entity)
        self.session.flush()
        return entity
