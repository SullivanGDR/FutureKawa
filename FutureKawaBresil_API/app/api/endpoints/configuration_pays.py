from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.configuration_pays import ConfigurationPaysCreate, ConfigurationPaysResponse
from app.crud import configuration_pays as crud_config

router = APIRouter(prefix="/configuration-pays", tags=["Configuration Pays"])

@router.post("/", response_model=ConfigurationPaysResponse)
async def create_configuration_pays(config: ConfigurationPaysCreate, db: AsyncSession = Depends(get_db)):
    return await crud_config.create_configuration_pays(db=db, config=config)

@router.get("/", response_model=List[ConfigurationPaysResponse])
async def read_configurations_pays(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_config.get_all_configurations_pays(db, skip=skip, limit=limit)

@router.get("/{nom_pays}", response_model=ConfigurationPaysResponse)
async def read_configuration_pays(nom_pays: str, db: AsyncSession = Depends(get_db)):
    db_config = await crud_config.get_configuration_pays(db, nom_pays=nom_pays)
    if db_config is None:
        raise HTTPException(status_code=404, detail="Configuration pays non trouvée")
    return db_config
