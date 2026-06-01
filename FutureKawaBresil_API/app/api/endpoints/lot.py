from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.lot import LotCreate, LotResponse
from app.crud import lot as crud_lot

router = APIRouter(prefix="/lots", tags=["Lots"])

@router.post("/", response_model=LotResponse)
async def create_lot(lot: LotCreate, db: AsyncSession = Depends(get_db)):
    return await crud_lot.create_lot(db=db, lot=lot)

@router.get("/", response_model=List[LotResponse])
async def read_lots(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_lot.get_all_lots(db, skip=skip, limit=limit)

@router.get("/{lot_id}", response_model=LotResponse)
async def read_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    db_lot = await crud_lot.get_lot(db, lot_id=lot_id)
    if db_lot is None:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return db_lot

@router.get("/entrepot/{entrepot_id}", response_model=List[LotResponse])
async def read_lots_by_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_lot.get_lots_by_entrepot(db, entrepot_id=entrepot_id)

@router.patch("/{lot_id}/statut", response_model=LotResponse)
async def update_statut(lot_id: str, statut: str, db: AsyncSession = Depends(get_db)):
    db_lot = await crud_lot.update_lot_statut(db, lot_id=lot_id, statut=statut)
    if db_lot is None:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return db_lot

@router.delete("/{lot_id}", response_model=LotResponse)
async def delete_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    db_lot = await crud_lot.delete_lot(db, lot_id=lot_id)
    if db_lot is None:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return db_lot
