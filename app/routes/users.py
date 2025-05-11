from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import settings
from ..database import get_db
from ..services.user_service import update_user, get_users, get_user_by_id

router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Пользователи"]
)

@router.get("/me", response_model=schemas.User)
def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Получает данные текущего аутентифицированного пользователя.
    
    Args:
        current_user (User): Текущий пользователь (из токена).
        
    Returns:
        User: Данные текущего пользователя.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет данные текущего пользователя.
    
    Args:
        user_update (UserUpdate): Новые данные пользователя.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        User: Обновленные данные пользователя.
    """
    return update_user(db, current_user.id, user_update)

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получает список всех пользователей (только для администраторов).
    
    Args:
        skip (int): Сколько записей пропустить (для пагинации).
        limit (int): Максимальное количество записей.
        current_user (User): Текущий пользователь (должен быть администратором).
        db (Session): Сессия базы данных.
        
    Returns:
        List[User]: Список пользователей.
    """
    return get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    current_user: models.User = Depends(security.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получает данные пользователя по ID (только для администраторов).
    
    Args:
        user_id (int): ID пользователя.
        current_user (User): Текущий пользователь (должен быть администратором).
        db (Session): Сессия базы данных.
        
    Returns:
        User: Данные запрошенного пользователя.
    """
    return get_user_by_id(db, user_id)