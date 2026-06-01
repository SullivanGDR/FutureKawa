from pydantic import BaseModel, ConfigDict

class ModuleIotBase(BaseModel):
    id_module: str
    statut_connexion: str
    id_entrepot: int

class ModuleIotCreate(ModuleIotBase):
    pass

class ModuleIotResponse(ModuleIotBase):
    model_config = ConfigDict(from_attributes=True)
