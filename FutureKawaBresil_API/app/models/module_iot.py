from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ModuleIot(Base):
    __tablename__ = "module_iot"

    id_module = Column(String(100), primary_key=True, index=True)
    statut_connexion = Column(String(50), nullable=False)
    id_entrepot = Column(Integer, ForeignKey("entrepot.id_entrepot"), nullable=False)

    entrepot = relationship("Entrepot", back_populates="modules")
    releves = relationship("ReleveMesure", back_populates="module")
    alertes = relationship("Alerte", back_populates="module")
