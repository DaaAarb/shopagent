"""Catálogo: consulta pública de productos, con filtro por categoría."""

import pytest

from app.models import ProductCategory
from app.services import ProductNotFound, ProductService


@pytest.fixture
def product_service(uow) -> ProductService:
    return ProductService(uow)


# --- Servicio --------------------------------------------------------------------


def test_list_products_is_sorted_by_name(product_service, make_product):
    make_product(name="Pelota Rebotona")
    make_product(name="Cuerda Tira y Afloja")

    names = [p.name for p in product_service.list_products()]

    assert names == ["Cuerda Tira y Afloja", "Pelota Rebotona"]


def test_list_products_filters_by_category(product_service, make_product):
    ball = make_product(category=ProductCategory.BALLS)
    make_product(category=ProductCategory.PLUSH)

    result = product_service.list_products(ProductCategory.BALLS)

    assert [p.id for p in result] == [ball.id]


def test_get_product_by_slug(product_service, make_product):
    make_product(slug="pelota-rebotona", name="Pelota Rebotona")

    product = product_service.get_product("pelota-rebotona")

    assert product.name == "Pelota Rebotona"


def test_get_unknown_slug_raises(product_service):
    with pytest.raises(ProductNotFound):
        product_service.get_product("no-existe")


# --- API -------------------------------------------------------------------------


def test_catalog_is_public(client, make_product):
    make_product()

    response = client.get("/products")  # sin cabecera X-User-Id

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_products_with_category_filter(client, make_product):
    make_product(category=ProductCategory.BALLS)
    make_product(category=ProductCategory.ROPE)

    response = client.get("/products", params={"category": "rope"})

    assert [p["category"] for p in response.json()] == ["rope"]


def test_unknown_category_returns_422(client):
    assert client.get("/products", params={"category": "coches"}).status_code == 422


def test_get_product_detail(client, make_product):
    product = make_product(slug="hueso-roedor", price_cents=999, stock=3)

    response = client.get("/products/hueso-roedor")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == product.id
    assert body["price_cents"] == 999
    assert body["stock"] == 3


def test_get_unknown_product_returns_404(client):
    assert client.get("/products/no-existe").status_code == 404
