from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Entrepot(Base):
    __tablename__ = "entrepot"

    id_entrepot = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom_entrepot = Column(String(150), nullable=False)

    lots = relationship("Lot", back_populates="entrepot")
    modules = relationship("ModuleIot", back_populates="entrepot")
