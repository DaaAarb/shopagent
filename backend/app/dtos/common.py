from typing import Annotated

from pydantic import StringConstraints

# Texto obligatorio, sin espacios en los extremos.
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
