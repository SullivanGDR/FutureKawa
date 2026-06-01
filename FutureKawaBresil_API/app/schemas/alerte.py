from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AlerteBase(BaseModel):
    type_alerte: str
    description: Optional[str] = None
    id_lot: Optional[str] = None
    id_entrepot: Optional[int] = None

class AlerteCreate(AlerteBase):
    pass

class AlerteResponse(AlerteBase):
    id_alerte: int
    date_alerte: datetime
    model_config = ConfigDict(from_attributes=True)
