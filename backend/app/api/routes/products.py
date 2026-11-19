from fastapi import APIRouter

from app.api.deps import ProductServiceDep
from app.dtos import ProductRead
from app.models import ProductCategory

# Rutas públicas: no piden sesión (el catálogo lo ve cualquiera).
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(products: ProductServiceDep, category: ProductCategory | None = None):
    # `category` no está en la ruta → FastAPI lo lee de la query: /products?category=balls
    # Al ser un enum, un valor inventado se rechaza solo con 422.
    return products.list_products(category)


@router.get("/{slug}", response_model=ProductRead)
def get_product(slug: str, products: ProductServiceDep):
    return products.get_product(slug)
