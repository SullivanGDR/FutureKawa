from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.module_iot import ModuleIot
from app.schemas.module_iot import ModuleIotCreate

async def get_module(db: AsyncSession, module_id: str):
    result = await db.execute(select(ModuleIot).filter(ModuleIot.id_module == module_id))
    return result.scalars().first()

async def get_all_modules(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(ModuleIot).offset(skip).limit(limit))
    return result.scalars().all()

async def get_modules_by_entrepot(db: AsyncSession, entrepot_id: int):
    result = await db.execute(select(ModuleIot).filter(ModuleIot.id_entrepot == entrepot_id))
    return result.scalars().all()

async def create_module(db: AsyncSession, module: ModuleIotCreate):
    db_module = ModuleIot(**module.model_dump())
    db.add(db_module)
    await db.commit()
    await db.refresh(db_module)
    return db_module

async def update_statut_connexion(db: AsyncSession, module_id: str, statut: str):
    db_module = await get_module(db, module_id)
    if db_module:
        db_module.statut_connexion = statut
        await db.commit()
        await db.refresh(db_module)
    return db_module

async def delete_module(db: AsyncSession, module_id: str):
    db_module = await get_module(db, module_id)
    if db_module:
        await db.delete(db_module)
        await db.commit()
    return db_module
