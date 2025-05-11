from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from . import models
from .database import engine
from .config import settings
from .routes import auth, users, items
from .templates import templates  # Импортируем настроенный шаблонизатор

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

# Инициализируем FastAPI приложение
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Бэкенд приложения на FastAPI",
    version="1.0.0",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Настройка CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем директорию со статичными файлами
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Подключаем маршруты API
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)

# Маршруты для статичных страниц
@app.get("/", include_in_schema=False)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная"})

@app.get("/about", include_in_schema=False)
async def about(request: Request):
    """О нас"""
    return templates.TemplateResponse("about.html", {"request": request, "title": "О нас"})

@app.get("/contact", include_in_schema=False)
async def contact(request: Request):
    """Контакты"""
    return templates.TemplateResponse("contact.html", {"request": request, "title": "Контакты"})

# Обработка ошибок
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """Обработка ошибки 404 - Страница не найдена"""
    return templates.TemplateResponse(
        "errors/404.html", {"request": request, "title": "Страница не найдена"}, status_code=404
    )

@app.get("/api", include_in_schema=False)
def api_root():
    """Корневой маршрут API для проверки работоспособности"""
    return {
        "message": "API успешно запущено",
        "documentation": f"{settings.API_V1_PREFIX}/docs"
    }