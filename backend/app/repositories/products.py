from app.models import Product
from app.repositories.base import Repository


class ProductRepository(Repository[Product]):
    """De momento solo usa lo genérico. El checkout añadirá aquí sus consultas
    (p. ej. bloquear las filas de stock con SELECT … FOR UPDATE)."""

    model = Product
