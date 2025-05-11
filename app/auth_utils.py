from passlib.context import CryptContext
from fastapi import HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.main import get_db

# Настройка контекста хеширования (алгоритм bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Возвращает хеш для указанного пароля."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает пароль в открытом виде с его хэшем, возвращает True если совпадают."""
    return pwd_context.verify(plain_password, hashed_password)

# Зависимость для получения текущего пользователя по сессии
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        # Если в сессии нет user_id, пользователь не авторизован
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    # Получаем пользователя из базы по ID
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# Зависимость для проверки прав администратора
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user