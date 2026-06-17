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
    NOM_PAYS: str = "Brésil"

    DATABASE_URL: str 

    # Configuration SMTP Mailtrap
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "alerts@futurekawa.com"
    MAIL_PORT: int = 2525
    MAIL_SERVER: str = "sandbox.smtp.mailtrap.io"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance des paramètres mis en cache."""
    return Settings()
