from passlib.context import CryptContext

# Настройка контекста хеширования (алгоритм bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Возвращает хеш для указанного пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает пароль в открытом виде с его хэшем, возвращает True если совпадают."""
    return pwd_context.verify(plain_password, hashed_password)
