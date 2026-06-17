from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id_utilisateur: int
    email: str
    nom: str
    role: str
    nom_pays: Optional[str] = None

    class Config:
        from_attributes = True
