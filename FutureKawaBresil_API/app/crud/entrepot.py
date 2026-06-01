from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.entrepot import Entrepot
from app.schemas.entrepot import EntrepotCreate

async def get_entrepot(db: AsyncSession, entrepot_id: int):
    result = await db.execute(select(Entrepot).filter(Entrepot.id_entrepot == entrepot_id))
    return result.scalars().first()

async def get_all_entrepots(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Entrepot).offset(skip).limit(limit))
    return result.scalars().all()

async def get_entrepots_by_pays(db: AsyncSession, pays_id: int):
    result = await db.execute(select(Entrepot).filter(Entrepot.id_pays == pays_id))
    return result.scalars().all()

async def create_entrepot(db: AsyncSession, entrepot: EntrepotCreate):
    db_entrepot = Entrepot(**entrepot.model_dump())
    db.add(db_entrepot)
    await db.commit()
    await db.refresh(db_entrepot)
    return db_entrepot

async def delete_entrepot(db: AsyncSession, entrepot_id: int):
    db_entrepot = await get_entrepot(db, entrepot_id)
    if db_entrepot:
        await db.delete(db_entrepot)
        await db.commit()
    return db_entrepot
