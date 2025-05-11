from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

# === Пользователи ===

class UserBase(BaseModel):
    """Базовая схема с общими полями пользователя."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    """Схема для создания пользователя."""
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)

class UserInDB(UserBase):
    """Схема пользователя, хранящегося в базе данных."""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class User(UserInDB):
    """Схема пользователя для ответов API."""
    pass

# === Элементы ===

class ItemBase(BaseModel):
    """Базовая схема элемента."""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class ItemCreate(ItemBase):
    """Схема для создания элемента."""
    pass

class ItemUpdate(BaseModel):
    """Схема для обновления элемента."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class ItemInDB(ItemBase):
    """Схема элемента, хранящегося в базе данных."""
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class Item(ItemInDB):
    """Схема элемента для ответов API."""
    pass

# === Токены ===

class Token(BaseModel):
    """Схема JWT токена."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Данные, хранимые в JWT токене."""
    username: Optional[str] = None