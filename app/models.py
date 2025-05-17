from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from typing import Optional, List
from datetime import datetime


# Создаем базовый класс для декларативных моделей SQLAlchemy 2.0
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(100), unique=True
    )  # Убираем index=True здесь
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")

    # Поля для отслеживания прогресса
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Отношения
    games_history: Mapped[List["GameSession"]] = relationship(
        "GameSession", back_populates="user"
    )

    # Определяем только один индекс через table_args, а не дублируем его
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),  # Указываем unique=True здесь
    )


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(100), nullable=False)
    scrambled: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    translation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(20), default="easy"
    )  # "easy", "medium", "hard"
    game_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "scramble", "matching", "typing"

    # Статистика использования
    times_shown: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    game_type: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Статистика сессии
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship("User", back_populates="games_history")


class GameSetting(Base):
    __tablename__ = "game_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
