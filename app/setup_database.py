from app.database import SessionLocal, engine
from app.models import Base, User, Word, GameSession, GameSetting
from app.password_utils import get_password_hash
import random
import string
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_scrambled_word(word):
    """Создает перемешанную версию слова для анаграмм."""
    chars = list(word)
    random.shuffle(chars)
    scrambled = "".join(chars).upper()

    # Если случайно получилось исходное слово - перемешиваем еще раз
    if scrambled.lower() == word.lower():
        return create_scrambled_word(word)

    return scrambled


def setup_database():
    """Настройка базы данных - создание таблиц и начальных данных."""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    # Создаем начальные данные (при необходимости)
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже пользователи в базе
        users_exist = db.query(User).first() is not None

        if not users_exist:
            logger.info("База данных пуста. Создаем тестовых пользователей...")

            # Создаем администратора
            admin = User(
                name="Администратор",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                role="admin",
            )
            db.add(admin)

            # Создаем обычного пользователя
            user = User(
                name="Тестовый пользователь",
                email="user@example.com",
                password_hash=get_password_hash("user123"),
                role="user",
                level=3,
                experience=50,
                total_points=250,
            )
            db.add(user)

            # Создаем пользователя с более высоким уровнем
            advanced_user = User(
                name="Продвинутый пользователь",
                email="advanced@example.com",
                password_hash=get_password_hash("password"),
                role="user",
                level=7,
                experience=75,
                total_points=750,
            )
            db.add(advanced_user)

            db.commit()
            logger.info(f"Созданы тестовые пользователи:")
            logger.info(f"Админ: admin@example.com / admin123")
            logger.info(f"Пользователь: user@example.com / user123")
            logger.info(f"Продвинутый пользователь: advanced@example.com / password")
        else:
            logger.info("База данных уже содержит пользователей.")

        # Проверяем наличие слов в базе
        words_exist = db.query(Word).first() is not None

        if not words_exist:
            logger.info("Создаем тестовые слова для игр...")

            # Слова для игры Анаграммы (scramble)
            scramble_words = [
                {"text": "apple", "difficulty": "easy"},
                {"text": "book", "difficulty": "easy"},
                {"text": "cat", "difficulty": "easy"},
                {"text": "house", "difficulty": "easy"},
                {"text": "computer", "difficulty": "medium"},
                {"text": "language", "difficulty": "medium"},
                {"text": "homework", "difficulty": "medium"},
                {"text": "knowledge", "difficulty": "hard"},
                {"text": "university", "difficulty": "hard"},
                {"text": "dictionary", "difficulty": "hard"},
            ]

            for word_data in scramble_words:
                word = Word(
                    text=word_data["text"],
                    scrambled=create_scrambled_word(word_data["text"]),
                    difficulty=word_data["difficulty"],
                    game_type="scramble",
                )
                db.add(word)

            # Слова для игры Сопоставление (matching)
            matching_words = [
                {"text": "apple", "translation": "яблоко", "difficulty": "easy"},
                {"text": "book", "translation": "книга", "difficulty": "easy"},
                {"text": "cat", "translation": "кошка", "difficulty": "easy"},
                {"text": "dog", "translation": "собака", "difficulty": "easy"},
                {"text": "house", "translation": "дом", "difficulty": "easy"},
                {"text": "window", "translation": "окно", "difficulty": "medium"},
                {"text": "table", "translation": "стол", "difficulty": "medium"},
                {
                    "text": "computer",
                    "translation": "компьютер",
                    "difficulty": "medium",
                },
                {"text": "language", "translation": "язык", "difficulty": "medium"},
                {"text": "knowledge", "translation": "знание", "difficulty": "hard"},
                {
                    "text": "university",
                    "translation": "университет",
                    "difficulty": "hard",
                },
                {"text": "dictionary", "translation": "словарь", "difficulty": "hard"},
            ]

            for word_data in matching_words:
                word = Word(
                    text=word_data["text"],
                    translation=word_data["translation"],
                    difficulty=word_data["difficulty"],
                    game_type="matching",
                )
                db.add(word)

            # Слова для игры Написание слов (typing)
            typing_words = [
                {
                    "text": "cat",
                    "description": "Домашнее животное, которое мяукает",
                    "difficulty": "easy",
                },
                {
                    "text": "dog",
                    "description": "Домашнее животное, которое лает",
                    "difficulty": "easy",
                },
                {
                    "text": "house",
                    "description": "Здание, в котором живут люди",
                    "difficulty": "easy",
                },
                {
                    "text": "book",
                    "description": "Предмет с текстом и страницами, который можно читать",
                    "difficulty": "easy",
                },
                {
                    "text": "computer",
                    "description": "Электронное устройство для обработки информации",
                    "difficulty": "medium",
                },
                {
                    "text": "window",
                    "description": "Прозрачная часть стены, через которую можно смотреть",
                    "difficulty": "medium",
                },
                {
                    "text": "table",
                    "description": "Предмет мебели с плоской поверхностью на ножках",
                    "difficulty": "medium",
                },
                {
                    "text": "language",
                    "description": "Система коммуникации, используемая людьми для общения",
                    "difficulty": "medium",
                },
                {
                    "text": "knowledge",
                    "description": "Факты, информация и навыки, приобретенные через опыт или обучение",
                    "difficulty": "hard",
                },
                {
                    "text": "university",
                    "description": "Высшее учебное заведение для обучения и исследований",
                    "difficulty": "hard",
                },
                {
                    "text": "dictionary",
                    "description": "Книга или электронный ресурс со словами и их значениями",
                    "difficulty": "hard",
                },
            ]

            for word_data in typing_words:
                word = Word(
                    text=word_data["text"],
                    description=word_data["description"],
                    difficulty=word_data["difficulty"],
                    game_type="typing",
                )
                db.add(word)

            db.commit()
            logger.info(f"Создано {len(scramble_words)} слов для анаграмм")
            logger.info(f"Создано {len(matching_words)} слов для сопоставления")
            logger.info(f"Создано {len(typing_words)} слов для написания")
        else:
            logger.info("База данных уже содержит слова для игр.")

        # Проверяем настройки игры
        settings_exist = db.query(GameSetting).first() is not None

        if not settings_exist:
            logger.info("Создаем настройки игры по умолчанию...")

            default_settings = [
                {"key": "points_per_answer", "value": "10"},
                {"key": "points_for_level_up", "value": "100"},
                {"key": "streak_bonus", "value": "5"},
                {"key": "max_level", "value": "10"},
                {"key": "scramble_time_limit", "value": "60"},
                {"key": "matching_time_limit", "value": "90"},
                {"key": "typing_time_limit", "value": "60"},
            ]

            for setting in default_settings:
                game_setting = GameSetting(key=setting["key"], value=setting["value"])
                db.add(game_setting)

            db.commit()
            logger.info("Настройки игры успешно созданы")
        else:
            logger.info("Настройки игры уже существуют в базе данных")

    except Exception as e:
        logger.error(f"Ошибка при настройке базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    setup_database()
