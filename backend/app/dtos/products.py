from pydantic import BaseModel, ConfigDict

from app.models import DogSize, ProductCategory

# --- Salida ---------------------------------------------------------------------


class ProductRead(BaseModel):
    """Ficha pública de un juguete del catálogo."""

    # Permite construirlo directamente desde la entidad: ProductRead.model_validate(product)
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    category: ProductCategory
    description: str
    price_cents: int
    # Se expone para que la tienda muestre "sin stock" o "quedan pocas unidades".
    stock: int
    material: str
    dog_size: DogSize
    image_url: str | None
    model_url: str | None
