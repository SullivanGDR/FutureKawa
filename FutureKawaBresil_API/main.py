from fastapi import FastAPI
from app.config import get_settings
from app.api.router import api_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API pour la gestion des entrepôts FutureKawa au Brésil"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "online"
    }
