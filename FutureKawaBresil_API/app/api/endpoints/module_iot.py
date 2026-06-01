from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.module_iot import ModuleIotCreate, ModuleIotResponse
from app.crud import module_iot as crud_module

router = APIRouter(prefix="/modules", tags=["Modules IoT"])

@router.post("/", response_model=ModuleIotResponse)
async def create_module(module: ModuleIotCreate, db: AsyncSession = Depends(get_db)):
    return await crud_module.create_module(db=db, module=module)

@router.get("/", response_model=List[ModuleIotResponse])
async def read_modules(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_module.get_all_modules(db, skip=skip, limit=limit)

@router.get("/{module_id}", response_model=ModuleIotResponse)
async def read_module(module_id: str, db: AsyncSession = Depends(get_db)):
    db_module = await crud_module.get_module(db, module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Module IoT non trouvé")
    return db_module

@router.get("/entrepot/{entrepot_id}", response_model=List[ModuleIotResponse])
async def read_modules_by_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_module.get_modules_by_entrepot(db, entrepot_id=entrepot_id)

@router.patch("/{module_id}/statut", response_model=ModuleIotResponse)
async def update_statut_connexion(module_id: str, statut: str, db: AsyncSession = Depends(get_db)):
    db_module = await crud_module.update_statut_connexion(db, module_id=module_id, statut=statut)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Module IoT non trouvé")
    return db_module

@router.delete("/{module_id}", response_model=ModuleIotResponse)
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db)):
    db_module = await crud_module.delete_module(db, module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Module IoT non trouvé")
    return db_module
