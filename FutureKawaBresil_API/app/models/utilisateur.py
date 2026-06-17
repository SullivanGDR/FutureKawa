from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    nom = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="employe")
    nom_pays = Column(String(50), ForeignKey("configuration_pays.nom_pays"), nullable=True)
