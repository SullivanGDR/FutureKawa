from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Paramètres globaux de l'application.
    Les valeurs peuvent être surchargées par le fichier .env
    """
    APP_NAME: str = "FutureKawaBresil API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str  # Obligatoire — défini dans le fichier .env uniquement

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance des paramètres mis en cache."""
    return Settings()
