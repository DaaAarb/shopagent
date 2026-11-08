from fastapi import FastAPI

app = FastAPI(
    title="ShopAgent",
    description="Agente de atención al cliente con tool use y reglas de negocio en el backend.",
    version="0.1.0-dev",
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Comprobación de vida: la usarán Docker y el despliegue en la semana 4."""
    return {"status": "ok"}
