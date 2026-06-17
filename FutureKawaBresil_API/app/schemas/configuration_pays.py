from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class ConfigurationPaysBase(BaseModel):
    nom_pays: str
    email_responsable: str
    temp_ideale: Decimal
    hum_ideale: Decimal
    tolerance_temp: Decimal
    tolerance_hum: Decimal

class ConfigurationPaysCreate(ConfigurationPaysBase):
    pass

class ConfigurationPaysResponse(ConfigurationPaysBase):
    model_config = ConfigDict(from_attributes=True)
