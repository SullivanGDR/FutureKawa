from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.releve_mesure import ReleveMesure
from app.schemas.releve_mesure import ReleveMesureCreate

async def get_releve(db: AsyncSession, releve_id: int):
    result = await db.execute(select(ReleveMesure).filter(ReleveMesure.id_releve == releve_id))
    return result.scalars().first()

async def get_all_releves(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(ReleveMesure).offset(skip).limit(limit))
    return result.scalars().all()

async def get_releves_by_module(db: AsyncSession, module_id: str):
    result = await db.execute(select(ReleveMesure).filter(ReleveMesure.id_module == module_id))
    return result.scalars().all()

async def create_releve(db: AsyncSession, releve: ReleveMesureCreate):
    db_releve = ReleveMesure(**releve.model_dump())
    db.add(db_releve)
    await db.commit()
    await db.refresh(db_releve)
    return db_releve

async def delete_releve(db: AsyncSession, releve_id: int):
    db_releve = await get_releve(db, releve_id)
    if db_releve:
        await db.delete(db_releve)
        await db.commit()
    return db_releve
