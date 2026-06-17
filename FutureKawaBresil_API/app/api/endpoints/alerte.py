from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.alerte import AlerteCreate, AlerteResponse
from app.crud import alerte as crud_alerte
from app.crud import module_iot as crud_module
from app.crud import entrepot as crud_entrepot
from app.crud import configuration_pays as crud_config
from app.crud import releve_mesure as crud_releve
from app.crud import lot as crud_lot

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

@router.post("/{alerte_id}/acquitter", response_model=AlerteResponse)
async def acquitter_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    db_alerte = await crud_alerte.get_alerte(db, alerte_id=alerte_id)
    if not db_alerte:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    if db_alerte.traitee:
        return db_alerte
        
    if "péremption" in db_alerte.type_alerte.lower() or "peremption" in db_alerte.type_alerte.lower():
        raise HTTPException(status_code=400, detail="Impossible d'acquitter: la péremption d'un lot est définitive et irréversible.")
    
    if db_alerte.id_module:
        module = await crud_module.get_module(db, db_alerte.id_module)
        if module:
            entrepot = await crud_entrepot.get_entrepot(db, module.id_entrepot)
            from sqlalchemy.future import select
            from app.models.configuration_pays import ConfigurationPays
            result = await db.execute(select(ConfigurationPays).limit(1))
            config = result.scalars().first()
            releves = await crud_releve.get_releves_by_module(db, module.id_module)
            
            if releves and config:
                dernier_releve = sorted(releves, key=lambda x: x.date_heure, reverse=True)[0]
                
                if (dernier_releve.temperature < config.seuil_temp_min or 
                    dernier_releve.temperature > config.seuil_temp_max or
                    dernier_releve.humidite < config.seuil_hum_min or 
                    dernier_releve.humidite > config.seuil_hum_max):
                    raise HTTPException(status_code=400, detail="Impossible d'acquitter: les dernières mesures sont toujours hors seuil.")
                
                db_alerte.traitee = True
                await db.commit()
                await db.refresh(db_alerte)

                lots = await crud_lot.get_lots_by_entrepot(db, entrepot.id_entrepot)
                for l in lots:
                    if l.statut == 'en alerte':
                        await crud_lot.update_lot_statut(db, l.id_lot, 'conforme')
                        
                return db_alerte

    db_alerte.traitee = True
    await db.commit()
    await db.refresh(db_alerte)
    
    if db_alerte.id_lot:
        await crud_lot.update_lot_statut(db, db_alerte.id_lot, 'conforme')

    return db_alerte

@router.get("/module/{module_id}", response_model=List[AlerteResponse])
async def read_alertes_by_module(module_id: str, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_alertes_by_module(db, module_id=module_id)

@router.get("/lot/{lot_id}", response_model=List[AlerteResponse])
async def read_alertes_by_lot(lot_id: str, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_alertes_by_lot(db, lot_id=lot_id)

@router.get("/entrepot/{entrepot_id}", response_model=List[AlerteResponse])
async def read_alertes_by_entrepot(entrepot_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_alerte.get_alertes_by_entrepot(db, entrepot_id=entrepot_id)

@router.delete("/{alerte_id}", response_model=AlerteResponse)
async def delete_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    db_alerte = await crud_alerte.delete_alerte(db, alerte_id=alerte_id)
    if db_alerte is None:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return db_alerte
