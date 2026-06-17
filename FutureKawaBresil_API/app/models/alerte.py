from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Boolean
from app.models.base import Base

class Alerte(Base):
    __tablename__ = "alerte"

    id_alerte = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_alerte = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type_alerte = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    id_lot = Column(String(50), ForeignKey("lot.id_lot"), nullable=True)
    id_module = Column(String(100), ForeignKey("module_iot.id_module"), nullable=True)
    traitee = Column(Boolean, server_default='0', default=False, nullable=False)

    lot = relationship("Lot", back_populates="alertes")
    module = relationship("ModuleIot", back_populates="alertes")
