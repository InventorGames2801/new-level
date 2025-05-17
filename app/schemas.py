from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Union
from datetime import datetime

# === Пользователи ===


class UserBase(BaseModel):
    """Базовая схема с общими полями пользователя."""

    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=4)


class UserProfile(UserBase):
    """Данные профиля пользователя для отображения."""

    id: int
    level: int
    experience: int
    total_points: int

    class Config:
        model_config = {"from_attributes": True}


class UserStats(BaseModel):
    """Статистика и достижения пользователя."""

    level: int
    experience: int
    total_points: int
    total_games: int
    correct_answers: int

    class Config:
        model_config = {"from_attributes": True}


# === Слова и игры ===


class WordBase(BaseModel):
    """Базовая схема слова."""

    text: str = Field(..., min_length=1, max_length=100)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    game_type: str = Field(..., pattern="^(scramble|matching|typing)$")


class WordCreate(WordBase):
    """Схема для создания слова."""

    scrambled: Optional[str] = None
    translation: Optional[str] = None
    description: Optional[str] = None

    @validator("scrambled", always=True)
    def ensure_scrambled_for_scramble_game(cls, v, values):
        """Проверяет, что для игры 'scramble' есть поле scrambled."""
        if values.get("game_type") == "scramble" and not v:
            from random import sample

            text = values.get("text", "")
            return "".join(sample(text, len(text))).upper()
        return v


class WordRead(WordBase):
    """Схема слова для ответов API."""

    id: int
    scrambled: Optional[str] = None
    translation: Optional[str] = None
    description: Optional[str] = None
    times_shown: int
    times_correct: int

    class Config:
        model_config = {"from_attributes": True}


# === Игровые сессии ===


class GameSessionBase(BaseModel):
    """Базовая схема игровой сессии."""

    game_type: str = Field(..., pattern="^(scramble|matching|typing)$")


class GameSessionCreate(GameSessionBase):
    """Схема для создания игровой сессии."""

    pass


class GameResult(BaseModel):
    """Результаты завершенной игры."""

    session_id: int
    score: int
    correct_answers: int
    total_questions: int
    experience_gained: int


class GameSessionRead(GameSessionBase):
    """Схема игровой сессии для ответов API."""

    id: int
    user_id: int
    score: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    correct_answers: int
    total_questions: int

    class Config:
        model_config = {"from_attributes": True}


# === Авторизация ===


class Token(BaseModel):
    """JWT токен."""

    access_token: str
    token_type: str = "bearer"


class LoginForm(BaseModel):
    """Форма входа."""

    email: EmailStr
    password: str
