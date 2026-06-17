from sqlalchemy import Column, Integer, String, DECIMAL, Numeric
from app.models.base import Base

class ConfigurationPays(Base):
    __tablename__ = "configuration_pays"

    nom_pays = Column(String(100), primary_key=True)
    email_responsable = Column(String(255), nullable=False)
    temp_ideale = Column(DECIMAL(5, 2), nullable=False)
    hum_ideale = Column(DECIMAL(5, 2), nullable=False)
    tolerance_temp = Column(DECIMAL(5, 2), nullable=False)
    tolerance_hum = Column(DECIMAL(5, 2), nullable=False)

    @property
    def seuil_temp_min(self):
        return self.temp_ideale - self.tolerance_temp

    @property
    def seuil_temp_max(self):
        return self.temp_ideale + self.tolerance_temp

    @property
    def seuil_hum_min(self):
        return self.hum_ideale - self.tolerance_hum

    @property
    def seuil_hum_max(self):
        return self.hum_ideale + self.tolerance_hum
