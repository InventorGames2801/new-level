from passlib.context import CryptContext
from fastapi import HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        # Сделано без raise_error=False, чтобы вызвать именно 401 ошибку, а не 403
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Возвращает текущего пользователя если он авторизован, иначе None.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return current_user
