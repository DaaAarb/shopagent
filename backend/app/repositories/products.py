from collections.abc import Collection

from sqlmodel import col, select

from app.models import Product, ProductCategory
from app.repositories.base import Repository


class ProductRepository(Repository[Product]):
    model = Product

    def list_catalog(self, category: ProductCategory | None = None) -> list[Product]:
        """Catálogo ordenado por nombre; filtrado por categoría si se indica."""
        conditions = [Product.category == category] if category is not None else []
        return self.find(*conditions, order_by=(col(Product.name),))

    def get_by_slug(self, slug: str) -> Product | None:
        return self.session.exec(select(Product).where(Product.slug == slug)).first()

    def lock_by_ids(self, product_ids: Collection[int]) -> list[Product]:
        """Los productos que existan de entre esos ids, BLOQUEADOS para escribir.

        `SELECT … FOR UPDATE`: las filas quedan bloqueadas hasta el commit/rollback
        de la transacción. Si dos compras del último ítem llegan a la vez, la segunda
        espera aquí y, cuando la primera confirma, lee el stock ya descontado.
        Se ordena por id para que todas las transacciones bloqueen en el mismo orden
        y no se queden esperándose mutuamente (deadlock).
        """
        statement = (
            select(Product)
            .where(col(Product.id).in_(product_ids))
            .order_by(col(Product.id))
            .with_for_update()
        )
        return list(self.session.exec(statement).all())
