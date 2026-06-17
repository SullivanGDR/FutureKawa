from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Lot(Base):
    __tablename__ = "lot"

    id_lot = Column(String(50), primary_key=True, index=True)
    date_stockage = Column(Date, nullable=False)
    statut = Column(String(50), nullable=False)
    id_entrepot = Column(Integer, ForeignKey("entrepot.id_entrepot"), nullable=False)

    entrepot = relationship("Entrepot", back_populates="lots")
    alertes = relationship("Alerte", back_populates="lot")
