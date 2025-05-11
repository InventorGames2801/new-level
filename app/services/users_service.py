from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas
from ..utils.password import get_password_hash
from ..utils.validators import email_exists, username_exists

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Создает нового пользователя.
    
    Args:
        db (Session): Сессия базы данных.
        user (UserCreate): Данные нового пользователя.
        
    Returns:
        User: Созданный пользователь.
        
    Raises:
        HTTPException: Если email или имя пользователя уже заняты.
    """
    # Проверяем, уникален ли email
    if email_exists(db, user.email):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Проверяем, уникально ли имя пользователя
    if username_exists(db, user.username):
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    # Создаем хеш пароля для безопасного хранения
    hashed_password = get_password_hash(user.password)
    
    # Создаем объект пользователя
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    
    # Сохраняем в базу данных
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(
    db: Session, user_id: int, user_update: schemas.UserUpdate
) -> models.User:
    """
    Обновляет данные пользователя.
    
    Args:
        db (Session): Сессия базы данных.
        user_id (int): ID пользователя для обновления.
        user_update (UserUpdate): Новые данные пользователя.
        
    Returns:
        User: Обновленный пользователь.
        
    Raises:
        HTTPException: Если пользователь не найден или данные не уникальны.
    """
    # Получаем пользователя из базы
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем email на уникальность, если он изменяется
    if user_update.email is not None and db_user.email != user_update.email:
        if email_exists(db, user_update.email, user_id):
            raise HTTPException(status_code=400, detail="Email уже занят")
        db_user.email = user_update.email
    
    # Проверяем имя пользователя на уникальность, если оно изменяется
    if user_update.username is not None and db_user.username != user_update.username:
        if username_exists(db, user_update.username, user_id):
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
        db_user.username = user_update.username
    
    # Обновляем пароль, если он предоставлен
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    # Сохраняем изменения
    db.commit()
    db.refresh(db_user)
    
    return db_user

def get_user_by_id(db: Session, user_id: int) -> models.User:
    """
    Получает пользователя по ID.
    
    Args:
        db (Session): Сессия базы данных.
        user_id (int): ID пользователя.
        
    Returns:
        User: Найденный пользователь.
        
    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """
    Получает список пользователей с пагинацией.
    
    Args:
        db (Session): Сессия базы данных.
        skip (int): Сколько записей пропустить (для пагинации).
        limit (int): Максимальное количество записей.
        
    Returns:
        List[User]: Список пользователей.
    """
    return db.query(models.User).offset(skip).limit(limit).all()