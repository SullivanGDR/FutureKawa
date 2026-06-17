from fastapi import APIRouter
from app.api.endpoints import (
    configuration_pays,
    entrepot,
    lot,
    module_iot,
    releve_mesure,
    alerte,
    auth,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(configuration_pays.router)
api_router.include_router(entrepot.router)
api_router.include_router(lot.router)
api_router.include_router(module_iot.router)
api_router.include_router(releve_mesure.router)
api_router.include_router(alerte.router)
