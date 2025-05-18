from sqlalchemy import asc, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from dotenv import load_dotenv
import os
import logging

import random
from datetime import datetime, time, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple

from app.config import settings
from app.models import User, UserWordHistory, Word, GameSession, GameSetting
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
    echo=settings.DEBUG,  # SQL-логи только если DEBUG=True
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

        if not admin_email or not admin_password:
            logger.warning(
                "ВНИМАНИЕ: Не установлены переменные ADMIN_EMAIL или ADMIN_PASSWORD!"
            )
            logger.warning(
                "Для безопасности приложения, необходимо установить эти переменные в .env файле"
            )
            logger.warning("Без этих переменных приложение не создаст администратора.")
            return False

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
                logger.info(f"Пароль администратора (из .env): {admin_password}")
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
        user.last_login = datetime.now(timezone.utc)
        db.commit()


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


def get_users_statistics(db: Session) -> Dict[str, Any]:
    """
    Получает статистику по пользователям системы.

    Returns:
        Словарь с различными статистическими показателями
    """
    # Общее количество пользователей
    total_users = db.query(func.count(User.id)).scalar() or 0

    # Количество пользователей, зарегистрированных за последние 30 дней
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    new_users_30_days = (
        db.query(func.count(User.id))
        .filter(User.created_at >= thirty_days_ago)
        .scalar()
        or 0
    )

    # Активные пользователи (с активностью за последние 7 дней)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_users = (
        db.query(func.count(User.id.distinct()))
        .filter(User.last_login >= seven_days_ago)
        .scalar()
        or 0
    )

    # Статистика по уровням
    level_stats = (
        db.query(User.level, func.count(User.id).label("count"))
        .group_by(User.level)
        .all()
    )

    level_distribution = {level: count for level, count in level_stats}

    return {
        "total_users": total_users,
        "new_users_30_days": new_users_30_days,
        "active_users_7_days": active_users,
        "level_distribution": level_distribution,
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
    db: Session,
    user_id: int,
    count: int = 5,
    difficulty: Optional[str] = None,
    excluded_ids: List[int] = None,
) -> List[Word]:
    """Gets random words for a game, always returning requested count of words"""

    query = db.query(Word)

    if difficulty:
        query = query.filter(Word.difficulty == difficulty)

    # Применяем исключения только если после этого останутся слова
    if excluded_ids:
        # Сначала проверим, сколько всего подходящих слов
        total_words = query.count()

        # Проверим, сколько слов останется после исключения
        remaining_words = query.filter(~Word.id.in_(excluded_ids)).count()

        # Применяем фильтр только если останется достаточно слов
        if remaining_words >= count:
            query = query.filter(~Word.id.in_(excluded_ids))

    available_words = query.all()

    # Если доступно слишком мало слов - берем все что есть
    if len(available_words) <= count:
        selected_words = available_words
    else:
        selected_words = random.sample(available_words, count)

    for word in selected_words:
        word.times_shown += 1
        word.last_used_at = datetime.now(timezone.utc)

    db.commit()
    return selected_words


def add_user_experience(
    db: Session, user_id: int, exp_points: int
) -> Tuple[User, bool, bool]:
    """
    Добавление очков опыта пользователю и проверка на повышение уровня.
    Возвращает кортеж: (пользователь, был_ли_повышен_уровень, достигнут_ли_дневной_лимит)
    """
    user = get_user(db, user_id)
    if not user:
        return None, False, False

    # Получаем настройки
    daily_exp_limit = get_game_setting_int(db, "daily_experience_limit", 200)
    exp_for_level_up = get_game_setting_int(db, "points_for_level_up", 100)

    # Проверяем, нужно ли сбросить счетчик дневного опыта
    today = datetime.now(timezone.utc).date()
    if user.daily_experience_updated_at:
        last_update_date = user.daily_experience_updated_at.date()
        if last_update_date < today:
            # Новый день - сбрасываем счетчик
            user.daily_experience = 0

    # Проверяем, достигнут ли дневной лимит
    daily_limit_reached = False
    if daily_exp_limit > 0:  # Если лимит установлен (0 = без ограничений)
        # Сколько опыта можно добавить в пределах лимита
        available_exp = daily_exp_limit - user.daily_experience
        if available_exp <= 0:
            # Лимит уже достигнут
            daily_limit_reached = True
            exp_to_add = 0
        else:
            # Можно добавить в пределах лимита
            exp_to_add = min(exp_points, available_exp)
            user.daily_experience += exp_to_add
    else:
        # Нет лимита
        exp_to_add = exp_points

    # Обновляем время последнего обновления
    user.daily_experience_updated_at = datetime.now(timezone.utc)

    # Добавляем опыт и обновляем общее количество очков
    user.experience += exp_to_add
    user.total_points += exp_to_add

    # Проверяем, достаточно ли опыта для повышения уровня
    level_up = False
    while user.experience >= exp_for_level_up:
        user.experience -= exp_for_level_up
        user.level += 1
        level_up = True

    db.commit()
    db.refresh(user)
    return user, level_up, daily_limit_reached


def update_word_stats(db: Session, word_id: int, correct: bool) -> None:
    """Обновление статистики слова после ответа пользователя."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if word:
        if correct:
            word.times_correct += 1
        db.commit()


def get_words_statistics(db: Session) -> Dict[str, Any]:
    """
    Получает расширенную статистику по словам системы.

    Returns:
        Словарь с различными статистическими показателями
    """
    # Общее количество слов
    total_words = db.query(func.count(Word.id)).scalar() or 0

    # Распределение по сложности
    difficulty_stats = (
        db.query(Word.difficulty, func.count(Word.id).label("count"))
        .group_by(Word.difficulty)
        .all()
    )

    difficulty_distribution = {diff: count for diff, count in difficulty_stats}

    # Наиболее часто используемые слова
    most_used_words = db.query(Word).order_by(desc(Word.times_shown)).limit(10).all()

    # Слова с наихудшим процентом правильных ответов (минимум 5 показов)
    problematic_words = (
        db.query(Word)
        .filter(Word.times_shown >= 5)
        .order_by(asc(Word.correct_ratio))
        .limit(10)
        .all()
    )

    # Статистика использования по дням
    current_date = datetime.now(timezone.utc).date()
    usage_stats = []

    for days_back in range(30):
        date = current_date - timedelta(days=days_back)
        start_of_day = datetime.combine(date, time.min)
        end_of_day = datetime.combine(date, time.max)

        count = (
            db.query(func.count(UserWordHistory.id))
            .filter(
                UserWordHistory.used_at >= start_of_day,
                UserWordHistory.used_at <= end_of_day,
            )
            .scalar()
            or 0
        )

        correct = (
            db.query(func.count(UserWordHistory.id))
            .filter(
                UserWordHistory.used_at >= start_of_day,
                UserWordHistory.used_at <= end_of_day,
                UserWordHistory.correct == True,
            )
            .scalar()
            or 0
        )

        usage_stats.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "total": count,
                "correct": correct,
                "ratio": correct / count if count > 0 else 0,
            }
        )

    return {
        "total_words": total_words,
        "difficulty_distribution": difficulty_distribution,
        "most_used_words": [
            {
                "id": word.id,
                "text": word.text,
                "times_shown": word.times_shown,
                "correct_ratio": word.correct_ratio,
            }
            for word in most_used_words
        ],
        "problematic_words": [
            {
                "id": word.id,
                "text": word.text,
                "times_shown": word.times_shown,
                "correct_ratio": word.correct_ratio,
            }
            for word in problematic_words
        ],
        "usage_stats": usage_stats,
    }


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
        session.completed_at = datetime.now(timezone.utc)

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
