from typing import Annotated

from pydantic import StringConstraints

# Texto obligatorio: se le quitan los espacios de los extremos y no puede quedar vacío.
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
