from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Index,
    Float,
    Boolean,
    UniqueConstraint,
)
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
    email: Mapped[str] = mapped_column(String(100), unique=True)
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
        "GameSession", back_populates="user", cascade="all, delete-orphan"
    )
    word_history: Mapped[List["UserWordHistory"]] = relationship(
        "UserWordHistory", back_populates="user", cascade="all, delete-orphan"
    )

    # Определяем только один индекс через table_args, а не дублируем его
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_created_at", "created_at"),
    )


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(100), nullable=False)
    translation: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Обязательный перевод для всех слов
    description: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Обязательное описание для всех слов
    difficulty: Mapped[str] = mapped_column(
        String(20), default="easy"
    )  # "easy", "medium", "hard"

    # Статистика использования
    times_shown: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    correct_ratio: Mapped[float] = mapped_column(Float, default=0.0)  # Для аналитики

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_words_difficulty", "difficulty"),
        Index("ix_words_times_shown", "times_shown"),
        Index("ix_words_created_at", "created_at"),
    )


class UserWordHistory(Base):
    __tablename__ = "user_word_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey("words.id"), index=True)
    used_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    correct: Mapped[bool] = mapped_column(Boolean, default=False)
    game_type: Mapped[str] = mapped_column(
        String(50)
    )  # Тип игры, в которой использовалось слово

    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="word_history")
    word: Mapped["Word"] = relationship("Word")

    __table_args__ = (
        # Комбинированный индекс для быстрого поиска по пользователю и времени
        Index("ix_user_word_history_user_time", "user_id", "used_at"),
        # Уникальное ограничение, чтобы слово не использовалось дважды в одно время
        UniqueConstraint("user_id", "word_id", "used_at", name="uq_user_word_used_at"),
    )


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
    avg_response_time: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Среднее время ответа в секундах
    difficulty_level: Mapped[str] = mapped_column(
        String(20), default="easy"
    )  # Сложность игровой сессии

    user: Mapped["User"] = relationship("User", back_populates="games_history")

    __table_args__ = (
        Index("ix_game_sessions_started_at", "started_at"),
        Index("ix_game_sessions_user_id", "user_id"),
    )


class GameSetting(Base):
    __tablename__ = "game_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="system")

    __table_args__ = (Index("ix_game_settings_category", "category"),)
