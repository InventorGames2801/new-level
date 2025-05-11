from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..config import settings
from ..database import get_db
from ..services.item_service import (
    create_item,
    get_user_items,
    get_item_by_id,
    update_item,
    delete_item,
)

router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/items",
    tags=["Элементы"]
)

@router.post("/", response_model=schemas.Item)
def create_user_item(
    item: schemas.ItemCreate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создает новый элемент для текущего пользователя.
    
    Args:
        item (ItemCreate): Данные нового элемента.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        Item: Созданный элемент.
    """
    return create_item(db, item, current_user.id)

@router.get("/", response_model=List[schemas.Item])
def read_user_items(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получает список элементов текущего пользователя.
    
    Args:
        skip (int): Сколько записей пропустить (для пагинации).
        limit (int): Максимальное количество записей.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        List[Item]: Список элементов пользователя.
    """
    return get_user_items(db, current_user.id, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.Item)
def read_user_item(
    item_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получает элемент по ID.
    
    Args:
        item_id (int): ID элемента.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        Item: Запрошенный элемент.
        
    Raises:
        HTTPException: Если элемент не найден или пользователь не имеет доступа.
    """
    item = get_item_by_id(db, item_id)
    
    # Проверяем, принадлежит ли элемент текущему пользователю или пользователь - админ
    if item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Нет доступа к этому элементу"
        )
    
    return item

@router.put("/{item_id}", response_model=schemas.Item)
def update_user_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет элемент по ID.
    
    Args:
        item_id (int): ID элемента.
        item_update (ItemUpdate): Новые данные элемента.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        Item: Обновленный элемент.
        
    Raises:
        HTTPException: Если элемент не найден или пользователь не имеет доступа.
    """
    item = get_item_by_id(db, item_id)
    
    # Проверяем, принадлежит ли элемент текущему пользователю или пользователь - админ
    if item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на редактирование этого элемента"
        )
    
    return update_item(db, item_id, item_update)

@router.delete("/{item_id}", response_model=schemas.Item)
def delete_user_item(
    item_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаляет элемент по ID.
    
    Args:
        item_id (int): ID элемента.
        current_user (User): Текущий пользователь (из токена).
        db (Session): Сессия базы данных.
        
    Returns:
        Item: Удаленный элемент.
        
    Raises:
        HTTPException: Если элемент не найден или пользователь не имеет доступа.
    """
    item = get_item_by_id(db, item_id)
    
    # Проверяем, принадлежит ли элемент текущему пользователю или пользователь - админ
    if item.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на удаление этого элемента"
        )
    
    return delete_item(db, item_id)