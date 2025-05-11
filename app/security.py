from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from . import models
from . import schemas
from .utils.password import verify_password

# Настройка для получения токена через форму OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")

def authenticate_user(db: Session, username: str, password: str):
    """
    Аутентифицирует пользователя по имени пользователя и паролю.
    
    Args:
        db (Session): Сессия базы данных.
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
        
    Returns:
        User | False: Объект пользователя или False, если аутентификация не удалась.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создает JWT токен доступа.
    
    Args:
        data (dict): Данные для включения в токен.
        expires_delta (timedelta, optional): Время жизни токена.
        
    Returns:
        str: Закодированный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    Получает текущего пользователя по токену.
    
    Args:
        db (Session): Сессия базы данных.
        token (str): JWT токен.
        
    Returns:
        User: Текущий аутентифицированный пользователь.
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
):
    """
    Проверяет, активен ли текущий пользователь.
    
    Args:
        current_user (User): Текущий аутентифицированный пользователь.
        
    Returns:
        User: Текущий активный пользователь.
        
    Raises:
        HTTPException: Если пользователь неактивен.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user

async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
):
    """
    Проверяет, имеет ли текущий пользователь права администратора.
    
    Args:
        current_user (User): Текущий аутентифицированный пользователь.
        
    Returns:
        User: Текущий пользователь с правами администратора.
        
    Raises:
        HTTPException: Если у пользователя нет прав администратора.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return current_user