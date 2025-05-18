from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    logger.info("Начало миграции базы данных...")

    # Проверяем, есть ли уже колонки daily_experience и daily_experience_updated_at
    with engine.connect() as conn:
        # Для SQLite
        if engine.url.drivername.startswith("sqlite"):
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]

            if "daily_experience" not in columns:
                logger.info("Добавление колонки daily_experience в таблицу users")
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN daily_experience INTEGER DEFAULT 0"
                    )
                )

            if "daily_experience_updated_at" not in columns:
                logger.info(
                    "Добавление колонки daily_experience_updated_at в таблицу users"
                )
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN daily_experience_updated_at TIMESTAMP"
                    )
                )

        # Для PostgreSQL
        elif engine.url.drivername.startswith("postgresql"):
            # Проверка наличия колонки daily_experience
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'daily_experience'"
                )
            )
            if not result.fetchone():
                logger.info("Добавление колонки daily_experience в таблицу users")
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN daily_experience INTEGER DEFAULT 0"
                    )
                )

            # Проверка наличия колонки daily_experience_updated_at
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'daily_experience_updated_at'"
                )
            )
            if not result.fetchone():
                logger.info(
                    "Добавление колонки daily_experience_updated_at в таблицу users"
                )
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN daily_experience_updated_at TIMESTAMP"
                    )
                )

        # Добавление настройки daily_experience_limit в game_settings, если её нет
        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM game_settings WHERE key = 'daily_experience_limit'"
            )
        )
        if result.scalar() == 0:
            logger.info("Добавление настройки daily_experience_limit")
            conn.execute(
                text(
                    "INSERT INTO game_settings (key, value, description, category) VALUES (:key, :value, :description, :category)"
                ),
                {
                    "key": "daily_experience_limit",
                    "value": "200",
                    "description": "Дневной лимит опыта (0 = без ограничений)",
                    "category": "gameplay",
                },
            )

        conn.commit()

    logger.info("Миграция базы данных успешно завершена")


if __name__ == "__main__":
    migrate_database()
