from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.auth import LoginRequest, UserResponse
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login", response_model=UserResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Utilisateur).filter(Utilisateur.email == payload.email))
    user = result.scalars().first()
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifiants de connexion incorrects."
        )
        
    return user
