from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional

class ReleveMesureBase(BaseModel):
    temperature: Decimal
    humidite: Decimal
    id_module: str

class ReleveMesureCreate(ReleveMesureBase):
    pass

class ReleveMesureResponse(ReleveMesureBase):
    id_releve: int
    date_heure: datetime
    model_config = ConfigDict(from_attributes=True)
