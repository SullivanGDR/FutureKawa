from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.releve_mesure import ReleveMesureCreate, ReleveMesureResponse
from app.crud import releve_mesure as crud_releve
from app.crud import module_iot as crud_module
from app.crud import entrepot as crud_entrepot
from app.crud import configuration_pays as crud_config
from app.crud import alerte as crud_alerte
from app.crud import lot as crud_lot
from app.schemas.alerte import AlerteCreate

router = APIRouter(prefix="/releves", tags=["Relevés de mesure"])

@router.post("/", response_model=ReleveMesureResponse)
async def create_releve(releve: ReleveMesureCreate, db: AsyncSession = Depends(get_db)):
    db_releve = await crud_releve.create_releve(db=db, releve=releve)

    module = await crud_module.get_module(db, releve.id_module)
    if module:
        if module.statut_connexion != 'actif':
            module.statut_connexion = 'actif'
            await db.commit()
            await db.refresh(module)

        entrepot = await crud_entrepot.get_entrepot(db, module.id_entrepot)
        if entrepot:
            from sqlalchemy.future import select
            from app.models.configuration_pays import ConfigurationPays
            result = await db.execute(select(ConfigurationPays).limit(1))
            config = result.scalars().first()
            if config:
                is_alert = False
                reasons = []
                if releve.temperature < config.seuil_temp_min or releve.temperature > config.seuil_temp_max:
                    is_alert = True
                    reasons.append(f"Température anormale: {releve.temperature}°C (Tolérance: {config.seuil_temp_min}-{config.seuil_temp_max}°C)")
                
                if releve.humidite < config.seuil_hum_min or releve.humidite > config.seuil_hum_max:
                    is_alert = True
                    reasons.append(f"Humidité anormale: {releve.humidite}% (Tolérance: {config.seuil_hum_min}-{config.seuil_hum_max}%)")
                
                if is_alert:
                    alerte_in = AlerteCreate(
                        type_alerte="Conditionnement",
                        description=" | ".join(reasons),
                        id_module=module.id_module,
                        id_lot=None
                    )
                    await crud_alerte.create_alerte(db, alerte_in)

                    from app.services.mail import send_climate_alert_email
                    await send_climate_alert_email(
                        session=db,
                        module_id=module.id_module,
                        nom_entrepot=entrepot.nom_entrepot,
                        nom_pays=config.nom_pays,
                        temperature=releve.temperature,
                        humidite=releve.humidite,
                        config=config,
                        reasons=reasons
                    )

                    lots = await crud_lot.get_lots_by_entrepot(db, entrepot.id_entrepot)
                    for l in lots:
                        if l.statut == 'conforme':
                            await crud_lot.update_lot_statut(db, l.id_lot, 'en alerte')

    return db_releve

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
