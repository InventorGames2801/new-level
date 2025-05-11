from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, security
from ..config import settings
from ..database import get_db
from ..services.user_service import create_user

router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Аутентификация"]
)

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового пользователя.
    
    Args:
        user (UserCreate): Данные нового пользователя.
        db (Session): Сессия базы данных.
        
    Returns:
        User: Зарегистрированный пользователь.
    """
    return create_user(db, user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Создает JWT токен доступа при успешной аутентификации.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Форма с именем пользователя и паролем.
        db (Session): Сессия базы данных.
        
    Returns:
        Token: JWT токен доступа.
        
    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}