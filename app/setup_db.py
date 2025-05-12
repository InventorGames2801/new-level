from app.database import SessionLocal, engine
from app.models import Base, User
from app.auth_utils import get_password_hash
import os

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
            print("База данных пуста. Создаем тестовых пользователей...")
            
            # Создаем администратора
            admin = User(
                name="Администратор",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
            
            # Создаем обычного пользователя
            user = User(
                name="Тестовый пользователь",
                email="user@example.com",
                password_hash=get_password_hash("user123"),
                role="user"
            )
            db.add(user)
            
            db.commit()
            print(f"Созданы тестовые пользователи:")
            print(f"Админ: admin@example.com / admin123")
            print(f"Пользователь: user@example.com / user123")
        else:
            print("База данных уже содержит пользователей.")
    
    except Exception as e:
        print(f"Ошибка при настройке базы данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()