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

async def get_alertes_by_entrepot(db: AsyncSession, entrepot_id: int):
    result = await db.execute(select(Alerte).filter(Alerte.id_entrepot == entrepot_id))
    return result.scalars().all()

async def get_alertes_by_lot(db: AsyncSession, lot_id: str):
    result = await db.execute(select(Alerte).filter(Alerte.id_lot == lot_id))
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
