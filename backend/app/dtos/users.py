from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    # from_attributes: permite construirlo desde una entidad con `UserRead.model_validate(user)`,
    # leyendo sus atributos (user.id, user.name…) en vez de un diccionario.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
