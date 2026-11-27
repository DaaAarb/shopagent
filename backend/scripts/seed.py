"""Vacía la BD de desarrollo y la rellena con datos de demo: `python scripts/seed.py`.

Los pedidos se crean con OrderService para que cumplan las mismas reglas que la app.
"""

import json
import sys
from pathlib import Path

# Permite ejecutarlo como script desde backend/ (hace importable el paquete `app`).
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlmodel import Session  # noqa: E402

from app.db.session import engine  # noqa: E402
from app.dtos import OrderCreate, OrderLineCreate  # noqa: E402
from app.models import Product, User  # noqa: E402
from app.repositories import UnitOfWork  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.services import OrderService  # noqa: E402

CATALOG_FILE = Path(__file__).with_name("catalog.json")

# Pública a propósito: aparece en la pantalla de login de la demo.
DEMO_PASSWORD = "loba1234"

USERS = [
    ("Lucía García", "lucia@example.com", "Calle Mayor 12, 46001 Valencia"),
    ("Marcos Pérez", "marcos@example.com", "Avenida del Puerto 45, 46023 Valencia"),
    ("Sofía Ruiz", "sofia@example.com", "Plaza de la Reina 3, 46003 Valencia"),
]

# (estado final, [(slug, cantidad), ...]); cubren todos los estados.
ORDERS: dict[str, list[tuple[str, list[tuple[str, int]]]]] = {
    "lucia@example.com": [
        ("delivered", [("pelota-rebotona", 2), ("hueso-roedor", 1)]),
        ("paid", [("lobito-de-peluche", 1)]),
        ("pending", [("cuerda-tira-y-afloja", 1), ("pelota-chirrio", 2)]),
    ],
    "marcos@example.com": [
        ("shipped", [("cuerda-tira-y-afloja", 2)]),
        ("cancelled", [("erizo-crujiente", 1)]),
        # Agota el stock del Cubo Premios.
        ("delivered", [("cubo-premios", 2)]),
    ],
    "sofia@example.com": [
        ("pending", [("aro-mordisquitos", 1), ("erizo-crujiente", 1)]),
    ],
}

STEPS = {
    "pending": [],
    "paid": ["pay_order"],
    "shipped": ["pay_order", "ship_order"],
    "delivered": ["pay_order", "ship_order", "deliver_order"],
    "cancelled": ["cancel_order"],
}


def reset_database() -> None:
    """Aplica las migraciones y vacía todas las tablas, reiniciando los ids."""
    command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
    with engine.begin() as connection:
        connection.execute(
            text('TRUNCATE "user", product, "order", orderitem, ticket RESTART IDENTITY CASCADE')
        )


def seed() -> None:
    reset_database()

    with Session(engine) as session:
        password_hash = hash_password(DEMO_PASSWORD)
        users = [User(name=name, email=email, password_hash=password_hash) for name, email, _ in USERS]
        products = [Product(**item) for item in json.loads(CATALOG_FILE.read_text("utf-8"))]
        session.add_all([*users, *products])
        session.commit()

        product_ids = {p.slug: p.id for p in products}
        addresses = {email: address for _, email, address in USERS}
        orders = OrderService(UnitOfWork(session))

        for user in users:
            for final_status, lines in ORDERS.get(user.email, []):
                order = orders.create_order(
                    user.id,
                    OrderCreate(
                        items=[
                            OrderLineCreate(product_id=product_ids[slug], quantity=qty)
                            for slug, qty in lines
                        ],
                        shipping_address=addresses[user.email],
                    ),
                )
                for step in STEPS[final_status]:
                    getattr(orders, step)(user.id, order.id)

        print(f"Base de datos de desarrollo lista (contraseña de todos: {DEMO_PASSWORD}):")
        for user in users:
            print(f"  {user.email:<22} {user.name}")
        print(f"  {len(products)} productos · {sum(len(o) for o in ORDERS.values())} pedidos")


if __name__ == "__main__":
    seed()
