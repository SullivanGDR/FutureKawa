from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.configuration_pays import ConfigurationPays
from app.schemas.configuration_pays import ConfigurationPaysCreate

async def get_configuration_pays(db: AsyncSession, nom_pays: str):
    result = await db.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == nom_pays))
    return result.scalars().first()

async def get_all_configurations_pays(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(ConfigurationPays).offset(skip).limit(limit))
    return result.scalars().all()

async def create_configuration_pays(db: AsyncSession, config: ConfigurationPaysCreate):
    result = await db.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == config.nom_pays))
    db_config = result.scalars().first()
    if db_config:
        db_config.email_responsable = config.email_responsable
        db_config.temp_ideale = config.temp_ideale
        db_config.hum_ideale = config.hum_ideale
        db_config.tolerance_temp = config.tolerance_temp
        db_config.tolerance_hum = config.tolerance_hum
    else:
        db_config = ConfigurationPays(**config.model_dump())
        db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config
