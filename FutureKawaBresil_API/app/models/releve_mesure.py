from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class ReleveMesure(Base):
    __tablename__ = "releve_mesure"

    id_releve = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_heure = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    temperature = Column(DECIMAL(5, 2), nullable=False)
    humidite = Column(DECIMAL(5, 2), nullable=False)
    id_module = Column(String(100), ForeignKey("module_iot.id_module"), nullable=False)

    module = relationship("ModuleIot", back_populates="releves")
