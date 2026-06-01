from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Alerte(Base):
    __tablename__ = "alerte"

    id_alerte = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_alerte = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type_alerte = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    id_lot = Column(String(50), ForeignKey("lot.id_lot"), nullable=True)
    id_entrepot = Column(Integer, ForeignKey("entrepot.id_entrepot"), nullable=True)

    # Relations
    lot = relationship("Lot", back_populates="alertes")
    entrepot = relationship("Entrepot", back_populates="alertes")
