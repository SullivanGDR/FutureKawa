from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class LotBase(BaseModel):
    id_lot: str
    date_stockage: date
    statut: str
    id_entrepot: int

class LotCreate(LotBase):
    pass

class LotResponse(LotBase):
    model_config = ConfigDict(from_attributes=True)
