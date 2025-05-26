"""
Base repository interface and implementation following DIP
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface"""
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def create(self, entity_data: dict) -> T:
        pass
    
    @abstractmethod
    def update(self, entity_id: int, entity_data: dict) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass

class SQLAlchemyRepository(BaseRepository[T]):
    """Concrete implementation using SQLAlchemy"""
    
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()
    
    def create(self, entity_data: dict) -> T:
        entity = self.model_class(**entity_data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, entity_id: int, entity_data: dict) -> Optional[T]:
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, entity_id: int) -> bool:
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        return self.db.query(self.model_class).offset(offset).limit(limit).all()