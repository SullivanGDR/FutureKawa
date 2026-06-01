from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.alerte import AlerteCreate, AlerteResponse
from app.crud import alerte as crud_alerte

router = APIRouter(prefix="/alertes", tags=["Alertes"])

@router.post("/", response_model=AlerteResponse)
async def create_alerte(alerte: AlerteCreate, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.create_alerte(db=db, alerte=alerte)

@router.get("/", response_model=List[AlerteResponse])
async def read_alertes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_all_alertes(db, skip=skip, limit=limit)

@router.get("/{alerte_id}", response_model=AlerteResponse)
async def read_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    db_alerte = await crud_alerte.get_alerte(db, alerte_id=alerte_id)
    if db_alerte is None:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return db_alerte

@router.get("/entrepot/{entrepot_id}", response_model=List[AlerteResponse])
async def read_alertes_by_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_alertes_by_entrepot(db, entrepot_id=entrepot_id)

@router.get("/lot/{lot_id}", response_model=List[AlerteResponse])
async def read_alertes_by_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_alertes_by_lot(db, lot_id=lot_id)

@router.delete("/{alerte_id}", response_model=AlerteResponse)
async def delete_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    db_alerte = await crud_alerte.delete_alerte(db, alerte_id=alerte_id)
    if db_alerte is None:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return db_alerte
