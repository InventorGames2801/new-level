# app/models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

# один общий Base для всех таблиц
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100))
    email         = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role          = Column(String(50), default="user")      # "user" | "admin"

class Word(Base):
    __tablename__ = "words"

    id   = Column(Integer, primary_key=True)
    text = Column(String(100), nullable=False)
    # добавьте при необходимости: язык, сложность и т. д.

class GameSetting(Base):
    __tablename__ = "game_settings"

    id    = Column(Integer, primary_key=True)
    key   = Column(String(50), unique=True, nullable=False)
    value = Column(String(100), nullable=False)
