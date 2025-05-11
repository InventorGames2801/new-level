from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas

def create_item(
    db: Session, item: schemas.ItemCreate, owner_id: int
) -> models.Item:
    """
    Создает новый элемент.
    
    Args:
        db (Session): Сессия базы данных.
        item (ItemCreate): Данные нового элемента.
        owner_id (int): ID владельца элемента.
        
    Returns:
        Item: Созданный элемент.
    """
    db_item = models.Item(**item.dict(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_user_items(
    db: Session, owner_id: int, skip: int = 0, limit: int = 100
) -> list[models.Item]:
    """
    Получает список элементов, принадлежащих пользователю.
    
    Args:
        db (Session): Сессия базы данных.
        owner_id (int): ID владельца элементов.
        skip (int): Сколько записей пропустить (для пагинации).
        limit (int): Максимальное количество записей.
        
    Returns:
        List[Item]: Список элементов.
    """
    return (
        db.query(models.Item)
        .filter(models.Item.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_item_by_id(db: Session, item_id: int) -> models.Item:
    """
    Получает элемент по ID.
    
    Args:
        db (Session): Сессия базы данных.
        item_id (int): ID элемента.
        
    Returns:
        Item: Найденный элемент.
        
    Raises:
        HTTPException: Если элемент не найден.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    return item

def update_item(
    db: Session, item_id: int, item_update: schemas.ItemUpdate
) -> models.Item:
    """
    Обновляет данные элемента.
    
    Args:
        db (Session): Сессия базы данных.
        item_id (int): ID элемента для обновления.
        item_update (ItemUpdate): Новые данные элемента.
        
    Returns:
        Item: Обновленный элемент.
        
    Raises:
        HTTPException: Если элемент не найден.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Обновляем поля, если они предоставлены
    if item_update.title is not None:
        db_item.title = item_update.title
    if item_update.description is not None:
        db_item.description = item_update.description
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

def delete_item(db: Session, item_id: int) -> models.Item:
    """
    Удаляет элемент.
    
    Args:
        db (Session): Сессия базы данных.
        item_id (int): ID элемента для удаления.
        
    Returns:
        Item: Удаленный элемент.
        
    Raises:
        HTTPException: Если элемент не найден.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Копируем объект перед удалением
    item_copy = schemas.Item.from_orm(db_item)
    
    db.delete(db_item)
    db.commit()
    
    return item_copy