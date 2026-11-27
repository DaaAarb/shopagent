from app.dtos import ProductRead
from app.models import ProductCategory
from app.repositories import UnitOfWork
from app.services.exceptions import ProductNotFound


class ProductService:
    """Consulta del catálogo. Es público, así que no recibe `user_id`."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def list_products(self, category: ProductCategory | None = None) -> list[ProductRead]:
        return [ProductRead.model_validate(p) for p in self.uow.products.list_catalog(category)]

    def get_product(self, slug: str) -> ProductRead:
        product = self.uow.products.get_by_slug(slug)
        if product is None:
            raise ProductNotFound(slug)
        return ProductRead.model_validate(product)
