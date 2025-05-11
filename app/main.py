from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routes import auth, user, admin

from models import Base

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)

# Подключаем шаблонизатор Jinja2, указывая папку с шаблонами
templates = Jinja2Templates(directory="templates")

# Middleware для сессий на основе cookies (HttpOnly). 
# Cookie будет назван "session_id", подписан secret_key и помечен как Secure и SameSite.
app.add_middleware(
    SessionMiddleware, 
    secret_key="SUPER_SECRET_KEY",       # секретный ключ для подписи cookie (должен храниться в секрете)
    session_cookie="session_id",         # имя cookie-сессии
    same_site="strict",                 # предотвращаем отправку cookie на сторонние сайты
    https_only=True                     # помечать cookie как Secure (только по HTTPS)
)

# (Опционально) Раздача статических файлов, если нужны (например, CSS, изображения)
app.mount("/static", StaticFiles(directory="static"), name="static")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://username:password@localhost:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Создаём таблицы в базе (если база еще пуста)
Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()