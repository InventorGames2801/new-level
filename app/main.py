from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from app.routes import auth, index, user, game, admin  # Добавлен импорт admin
from app.config import settings
from app.templates import templates
from app.setup_database import setup_database

# Настройка логирования
level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(
    level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Приложение для изучения английского через игры",
    debug=settings.DEBUG,
)

# Регистрация роутеров
app.include_router(auth.router)  # Маршруты аутентификации
app.include_router(index.router)  # Основные маршруты (главная страница)
app.include_router(user.router)  # Маршруты профиля пользователя
app.include_router(game.router)  # Маршруты игрового процесса
app.include_router(admin.router)  # Маршруты администратора (добавлено)

# Настройка middleware для сессий
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session_id",
    same_site="lax",  # Более безопасное значение "strict" ограничивает использование в iframe
    https_only=(
        False if settings.DEBUG else True
    ),  # В отладке разрешаем HTTP, в production только HTTPS
)

# Создаем директорию для статических файлов в правильном месте
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Создана директория для статических файлов: {static_dir.absolute()}")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Проверяем наличие директории шаблонов
template_dir = None
try:
    # В новых версиях путь можно получить через loader.searchpath
    if (
        hasattr(templates, "env")
        and hasattr(templates.env, "loader")
        and hasattr(templates.env.loader, "searchpath")
    ):
        template_dir = templates.env.loader.searchpath[0]  # Первый путь из списка
    # В случае ошибки используем предполагаемый путь
    if not template_dir:
        template_dir = str(BASE_DIR / "templates")
except Exception as e:
    logger.warning(f"Не удалось определить путь к шаблонам: {e}")
    template_dir = str(BASE_DIR / "templates")

# Проверяем существование директории шаблонов
template_path = Path(template_dir)
if not template_path.exists():
    template_path.mkdir(exist_ok=True)
    logger.info(f"Создана директория для шаблонов: {template_path.absolute()}")

# Печатаем информацию о путях для отладки
logger.info(f"Базовая директория: {BASE_DIR}")
logger.info(f"Директория статических файлов: {static_dir}")
logger.info(f"Директория шаблонов: {template_dir}")
logger.info(f"DEBUG режим: {settings.DEBUG}")
logger.info(f"Автоматическая инициализация БД: {settings.INIT_DB}")


# Обработчик запуска приложения
@app.on_event("startup")
async def startup_event():
    """
    Выполняется при запуске приложения.
    Инициализирует базу данных, если это включено.
    """
    logger.info("Приложение запускается...")

    # Инициализируем базу данных, если включен флаг INIT_DB
    if settings.INIT_DB:
        try:
            logger.info("Инициализация базы данных...")
            setup_database()
            logger.info("✓ База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"✗ Ошибка при инициализации базы данных: {e}")
    else:
        logger.info("Инициализация базы данных отключена через настройки")


# Корневой маршрут для проверки работы API
@app.get("/api/health")
async def health_check():
    """
    Простой маршрут для проверки работоспособности API.
    """
    return {
        "status": "ok",
        "message": "API работает",
        "debug": settings.DEBUG,
        "paths": {
            "base_dir": str(BASE_DIR),
            "static_dir": str(static_dir),
            "templates_dir": str(template_dir),
        },
        "environment": {
            "init_db": settings.INIT_DB,
            "api_prefix": settings.API_V1_PREFIX,
            "project_name": settings.PROJECT_NAME,
        },
    }
