from app.database import SessionLocal, engine
from app.models import Base, User, Word, GameSession, GameSetting
from app.password_utils import get_password_hash
import random
from datetime import datetime, timezone
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
    try:
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы успешно созданы.")

        # Создаем начальные данные
        db = SessionLocal()

        try:
            # Получаем данные администратора из переменных окружения
            admin_name = os.getenv("ADMIN_NAME", "Администратор")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

            # Проверяем наличие значений
            if not admin_email or not admin_password:
                logger.warning("Не указаны переменные ADMIN_EMAIL или ADMIN_PASSWORD")
                admin_email = "admin@example.com"
                admin_password = "admin123"

            # Проверяем, существует ли администратор
            existing_admin = (
                db.query(User)
                .filter(User.email == admin_email, User.role == "admin")
                .first()
            )

            if not existing_admin:
                # Проверим, существует ли пользователь с таким email, но не admin
                existing_user = db.query(User).filter(User.email == admin_email).first()
                if existing_user:
                    # Если пользователь существует, но не admin - сделаем его админом
                    existing_user.role = "admin"
                    existing_user.name = admin_name
                    existing_user.password_hash = get_password_hash(admin_password)
                    db.commit()
                    logger.info(
                        f"Существующий пользователь обновлен до администратора:"
                    )
                    logger.info(f"  Email: {admin_email}")
                    logger.info(f"  Пароль: {admin_password}")
                else:
                    # Создаем нового администратора
                    hashed_password = get_password_hash(admin_password)
                    admin = User(
                        name=admin_name,
                        email=admin_email,
                        password_hash=hashed_password,
                        role="admin",
                        level=1,
                        experience=0,
                        total_points=0,
                        created_at=datetime.now(timezone.utc),
                    )
                    db.add(admin)
                    db.commit()
                    logger.info(f"Администратор успешно создан:")
                    logger.info(f"  Email: {admin_email}")
                    logger.info(f"  Пароль: {admin_password}")
            else:
                # Обновляем существующего администратора
                existing_admin.name = admin_name
                existing_admin.password_hash = get_password_hash(admin_password)
                db.commit()
                logger.info(f"Данные администратора обновлены согласно .env:")
                logger.info(f"  Email: {admin_email}")
                logger.info(f"  Пароль: {admin_password}")

            # [Остальной код для слов и настроек остается без изменений]

        except Exception as inner_error:
            logger.error(f"Внутренняя ошибка при настройке данных: {inner_error}")
            db.rollback()
        finally:
            db.close()

        return True
    except Exception as outer_error:
        logger.error(f"Ошибка при настройке базы данных: {outer_error}")
        return False


if __name__ == "__main__":
    setup_database()
