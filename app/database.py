from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from dotenv import load_dotenv
import os
import logging

import random
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from app.models import User, Word, GameSession, GameSetting
from app.password_utils import get_password_hash

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем URL подключения к базе данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем наличие URL
if not DATABASE_URL:
    logger.warning("DATABASE_URL не указан. Используется SQLite в памяти.")
    DATABASE_URL = "sqlite:///:memory:"

# Создаем движок базы данных с отладочной информацией
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Включаем вывод SQL-запросов для отладки
    # Для SQLite нужно убедиться, что check_same_thread=False
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Создает и возвращает сессию базы данных,
    автоматически закрывая ее после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    try:
        from app.models import Base

        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы успешно созданы.")

        admin_name = os.getenv("ADMIN_NAME")
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_name and admin_email and admin_password:
            db = SessionLocal()
            existing = db.query(User).filter(User.email == admin_email).first()
            if not existing:
                hashed_password = get_password_hash(admin_password)
                admin = User(
                    name=admin_name,
                    email=admin_email,
                    password_hash=hashed_password,
                    role="admin",
                )
                db.add(admin)
                db.commit()
                logger.info(
                    f"Администратор успешно создан:\n"
                    f"  Email: {admin_email}\n"
                    f"  Пароль: {admin_password}"
                )
            else:
                logger.info(f"Администратор уже существует: {admin_email}.")
                # (Не рекомендуется!) Если хотите, можно дополнительно вывести текущий пароль из env:
                # logger.info(f"Пароль администратора (из .env): {admin_password}")
            db.close()
        else:
            logger.warning(
                "Не указаны переменные ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD"
            )
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        return False


# === Пользователи ===


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получение пользователя по ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получение пользователя по email."""
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session, name: str, email: str, password: str, role: str = "user"
) -> User:
    """Создание нового пользователя."""
    hashed_password = get_password_hash(password)
    user = User(name=name, email=email, password_hash=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Обновление данных пользователя."""
    user = get_user(db, user_id)
    if not user:
        return None

    # Обновляем только переданные поля
    for key, value in kwargs.items():
        if key == "password":
            user.password_hash = get_password_hash(value)
        elif hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def update_user_last_login(db: Session, user_id: int) -> None:
    """Обновление времени последнего входа."""
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


def add_user_experience(
    db: Session, user_id: int, exp_points: int
) -> Tuple[User, bool]:
    """
    Добавление очков опыта пользователю и проверка на повышение уровня.
    Возвращает пользователя и флаг, указывающий было ли повышение уровня.
    """
    user = get_user(db, user_id)
    if not user:
        return None, False

    # Получаем настройки для повышения уровня
    exp_for_level_up = get_game_setting_int(db, "points_for_level_up", 100)

    # Добавляем опыт и обновляем общее количество очков
    user.experience += exp_points
    user.total_points += exp_points

    # Проверяем, достаточно ли опыта для повышения уровня
    level_up = False
    while user.experience >= exp_for_level_up:
        user.experience -= exp_for_level_up
        user.level += 1
        level_up = True

    db.commit()
    db.refresh(user)
    return user, level_up


def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Получение статистики игр пользователя."""
    user = get_user(db, user_id)
    if not user:
        return None

    # Получаем общее количество игр
    total_games = (
        db.query(func.count(GameSession.id))
        .filter(GameSession.user_id == user_id)
        .scalar()
        or 0
    )

    # Получаем общее количество правильных ответов
    correct_answers = (
        db.query(func.sum(GameSession.correct_answers))
        .filter(GameSession.user_id == user_id)
        .scalar()
        or 0
    )

    return {
        "level": user.level,
        "experience": user.experience,
        "total_points": user.total_points,
        "total_games": total_games,
        "correct_answers": correct_answers,
    }


# === Слова ===


def create_word(db: Session, **kwargs) -> Word:
    """Создание нового слова в базе."""
    word = Word(**kwargs)
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


def get_random_words(
    db: Session, game_type: str, count: int = 5, difficulty: Optional[str] = None
) -> List[Word]:
    """Получение случайных слов для игры с заданными параметрами."""
    query = db.query(Word).filter(Word.game_type == game_type)

    if difficulty:
        query = query.filter(Word.difficulty == difficulty)

    # Получаем все подходящие слова
    words = query.all()

    # Если слов меньше, чем запрошено, вернем все что есть
    if len(words) <= count:
        return words

    # Выбираем случайные слова с учетом статистики
    # Слова, которые показывались меньше, имеют больший шанс быть выбранными
    weighted_words = []
    for word in words:
        # Базовый вес для всех слов
        weight = 10
        # Уменьшаем вес для часто показываемых слов (но не меньше 1)
        if word.times_shown > 0:
            weight = max(1, weight - min(9, word.times_shown))
        weighted_words.extend([word] * weight)

    # Выбираем случайные слова
    selected = []
    remaining = weighted_words.copy()

    for _ in range(min(count, len(words))):
        if not remaining:
            break
        chosen = random.choice(remaining)
        # Удаляем все экземпляры выбранного слова, чтобы избежать дубликатов
        remaining = [w for w in remaining if w.id != chosen.id]
        selected.append(chosen)

    # Увеличиваем счетчик показов для выбранных слов
    for word in selected:
        word.times_shown += 1
    db.commit()

    return selected


def update_word_stats(db: Session, word_id: int, correct: bool) -> None:
    """Обновление статистики слова после ответа пользователя."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if word:
        if correct:
            word.times_correct += 1
        db.commit()


# === Игровые сессии ===


def create_game_session(db: Session, user_id: int, game_type: str) -> GameSession:
    """Создание новой игровой сессии."""
    session = GameSession(user_id=user_id, game_type=game_type)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def complete_game_session(
    db: Session, session_id: int, score: int, correct_answers: int, total_questions: int
) -> GameSession:
    """Завершение игровой сессии и запись результатов."""
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session:
        session.score = score
        session.correct_answers = correct_answers
        session.total_questions = total_questions
        session.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(session)
    return session


def get_user_game_history(
    db: Session, user_id: int, limit: int = 10
) -> List[GameSession]:
    """Получение истории игр пользователя."""
    return (
        db.query(GameSession)
        .filter(GameSession.user_id == user_id)
        .order_by(desc(GameSession.started_at))
        .limit(limit)
        .all()
    )


# === Настройки игры ===


def get_game_setting(db: Session, key: str, default: str = "") -> str:
    """Получение настройки игры по ключу."""
    setting = db.query(GameSetting).filter(GameSetting.key == key).first()
    return setting.value if setting else default


def get_game_setting_int(db: Session, key: str, default: int = 0) -> int:
    """Получение числовой настройки игры по ключу."""
    value = get_game_setting(db, key, str(default))
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def set_game_setting(db: Session, key: str, value: str) -> GameSetting:
    """Установка настройки игры."""
    setting = db.query(GameSetting).filter(GameSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = GameSetting(key=key, value=value)
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return setting


def get_all_game_settings(db: Session) -> Dict[str, str]:
    """Получение всех настроек игры."""
    settings = db.query(GameSetting).all()
    return {setting.key: setting.value for setting in settings}
