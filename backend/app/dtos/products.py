from pydantic import BaseModel, ConfigDict

from app.models import DogSize, ProductCategory

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    category: ProductCategory
    description: str
    price_cents: int
    stock: int
    material: str
    dog_size: DogSize
    image_url: str | None
    model_url: str | None
