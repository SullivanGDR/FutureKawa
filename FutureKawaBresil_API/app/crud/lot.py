from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.lot import Lot
from app.schemas.lot import LotCreate

async def get_lot(db: AsyncSession, lot_id: str):
    result = await db.execute(select(Lot).filter(Lot.id_lot == lot_id))
    return result.scalars().first()

async def get_all_lots(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Lot).offset(skip).limit(limit))
    return result.scalars().all()

async def get_lots_by_entrepot(db: AsyncSession, entrepot_id: int):
    result = await db.execute(select(Lot).filter(Lot.id_entrepot == entrepot_id))
    return result.scalars().all()

async def create_lot(db: AsyncSession, lot: LotCreate):
    db_lot = Lot(**lot.model_dump())
    db.add(db_lot)
    await db.commit()
    await db.refresh(db_lot)
    return db_lot

async def update_lot_statut(db: AsyncSession, lot_id: str, statut: str):
    db_lot = await get_lot(db, lot_id)
    if db_lot:
        db_lot.statut = statut
        await db.commit()
        await db.refresh(db_lot)
    return db_lot

async def delete_lot(db: AsyncSession, lot_id: str):
    db_lot = await get_lot(db, lot_id)
    if db_lot:
        await db.delete(db_lot)
        await db.commit()
    return db_lot
