from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.entrepot import EntrepotCreate, EntrepotResponse
from app.crud import entrepot as crud_entrepot

router = APIRouter(prefix="/entrepots", tags=["Entrepôts"])

@router.post("/", response_model=EntrepotResponse)
async def create_entrepot(entrepot: EntrepotCreate, db: AsyncSession = Depends(get_db)):
    return await crud_entrepot.create_entrepot(db=db, entrepot=entrepot)

@router.get("/", response_model=List[EntrepotResponse])
async def read_entrepots(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_entrepot.get_all_entrepots(db, skip=skip, limit=limit)

@router.get("/{entrepot_id}", response_model=EntrepotResponse)
async def read_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    db_entrepot = await crud_entrepot.get_entrepot(db, entrepot_id=entrepot_id)
    if db_entrepot is None:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    return db_entrepot

@router.get("/pays/{pays_id}", response_model=List[EntrepotResponse])
async def read_entrepots_by_pays(pays_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_entrepot.get_entrepots_by_pays(db, pays_id=pays_id)

@router.delete("/{entrepot_id}", response_model=EntrepotResponse)
async def delete_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    db_entrepot = await crud_entrepot.delete_entrepot(db, entrepot_id=entrepot_id)
    if db_entrepot is None:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    return db_entrepot
