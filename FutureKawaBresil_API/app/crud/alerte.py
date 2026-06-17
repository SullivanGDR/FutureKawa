from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.alerte import Alerte
from app.schemas.alerte import AlerteCreate

async def get_alerte(db: AsyncSession, alerte_id: int):
    result = await db.execute(select(Alerte).filter(Alerte.id_alerte == alerte_id))
    return result.scalars().first()

async def get_all_alertes(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Alerte).offset(skip).limit(limit))
    return result.scalars().all()

async def get_alertes_by_module(db: AsyncSession, module_id: str):
    result = await db.execute(select(Alerte).filter(Alerte.id_module == module_id))
    return result.scalars().all()

async def get_alertes_by_lot(db: AsyncSession, lot_id: str):
    result = await db.execute(select(Alerte).filter(Alerte.id_lot == lot_id))
    return result.scalars().all()

from app.models.lot import Lot
from app.models.module_iot import ModuleIot
from sqlalchemy import or_

async def get_alertes_by_entrepot(db: AsyncSession, entrepot_id: int):
    result = await db.execute(
        select(Alerte)
        .outerjoin(Lot, Alerte.id_lot == Lot.id_lot)
        .outerjoin(ModuleIot, Alerte.id_module == ModuleIot.id_module)
        .filter(or_(Lot.id_entrepot == entrepot_id, ModuleIot.id_entrepot == entrepot_id))
    )
    return result.scalars().all()

async def create_alerte(db: AsyncSession, alerte: AlerteCreate):
    db_alerte = Alerte(**alerte.model_dump())
    db.add(db_alerte)
    await db.commit()
    await db.refresh(db_alerte)
    return db_alerte

async def delete_alerte(db: AsyncSession, alerte_id: int):
    db_alerte = await get_alerte(db, alerte_id)
    if db_alerte:
        await db.delete(db_alerte)
        await db.commit()
    return db_alerte
