from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy.
    Permet à SQLAlchemy de collecter les métadonnées de l'ensemble des tables.
    """
    pass
