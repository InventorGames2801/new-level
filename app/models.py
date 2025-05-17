from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime

# один общий Base для всех таблиц
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(50), default="user")  # "user" | "admin"

    # Поля для отслеживания прогресса
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    total_points = Column(Integer, default=0)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Отношения
    games_history = relationship("GameSession", back_populates="user")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    text = Column(String(100), nullable=False)
    scrambled = Column(String(100), nullable=True)  # Перемешанная версия для анаграмм
    translation = Column(String(100), nullable=True)  # Перевод для режима сопоставления
    description = Column(String(255), nullable=True)  # Описание для режима написания
    difficulty = Column(String(20), default="easy")  # "easy", "medium", "hard"
    game_type = Column(String(50), nullable=False)  # "scramble", "matching", "typing"

    # Статистика использования
    times_shown = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String(50), nullable=False)  # "scramble", "matching", "typing"
    score = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Статистика сессии
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)

    user = relationship("User", back_populates="games_history")


class GameSetting(Base):
    __tablename__ = "game_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(String(100), nullable=False)
