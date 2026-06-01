from pydantic import BaseModel, ConfigDict
from typing import Optional

class EntrepotBase(BaseModel):
    nom_entrepot: str
    id_pays: int

class EntrepotCreate(EntrepotBase):
    pass

class EntrepotResponse(EntrepotBase):
    id_entrepot: int
    model_config = ConfigDict(from_attributes=True)
