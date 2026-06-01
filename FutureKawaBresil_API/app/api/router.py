from fastapi import APIRouter
from app.api.endpoints import (
    pays_exploitation,
    entrepot,
    lot,
    module_iot,
    releve_mesure,
    alerte,
)

api_router = APIRouter()

api_router.include_router(pays_exploitation.router)
api_router.include_router(entrepot.router)
api_router.include_router(lot.router)
api_router.include_router(module_iot.router)
api_router.include_router(releve_mesure.router)
api_router.include_router(alerte.router)
