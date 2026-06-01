from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.releve_mesure import ReleveMesureCreate, ReleveMesureResponse
from app.crud import releve_mesure as crud_releve

router = APIRouter(prefix="/releves", tags=["Relevés de mesure"])

@router.post("/", response_model=ReleveMesureResponse)
async def create_releve(releve: ReleveMesureCreate, db: AsyncSession = Depends(get_db)):
    return await crud_releve.create_releve(db=db, releve=releve)

@router.get("/", response_model=List[ReleveMesureResponse])
async def read_releves(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_releve.get_all_releves(db, skip=skip, limit=limit)

@router.get("/{releve_id}", response_model=ReleveMesureResponse)
async def read_releve(releve_id: int, db: AsyncSession = Depends(get_db)):
    db_releve = await crud_releve.get_releve(db, releve_id=releve_id)
    if db_releve is None:
        raise HTTPException(status_code=404, detail="Relevé non trouvé")
    return db_releve

@router.get("/module/{module_id}", response_model=List[ReleveMesureResponse])
async def read_releves_by_module(module_id: str, db: AsyncSession = Depends(get_db)):
    return await crud_releve.get_releves_by_module(db, module_id=module_id)

@router.delete("/{releve_id}", response_model=ReleveMesureResponse)
async def delete_releve(releve_id: int, db: AsyncSession = Depends(get_db)):
    db_releve = await crud_releve.delete_releve(db, releve_id=releve_id)
    if db_releve is None:
        raise HTTPException(status_code=404, detail="Relevé non trouvé")
    return db_releve
