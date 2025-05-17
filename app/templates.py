from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# Получаем абсолютный путь к директории templates
try:
    # Основной путь - рядом с текущим файлом
    templates_dir = Path(__file__).parent / "templates"

    # Убедимся, что директория существует
    if not templates_dir.exists():
        logger.warning(f"Директория шаблонов не найдена по пути: {templates_dir}")

        # Попробуем альтернативный путь - в корне проекта
        alt_path = Path(__file__).parent.parent / "templates"
        if alt_path.exists():
            logger.info(f"Используем альтернативный путь для шаблонов: {alt_path}")
            templates_dir = alt_path
        else:
            # Если директории нет, создадим пустую для избежания ошибок
            logger.warning(f"Создаем пустую директорию для шаблонов: {templates_dir}")
            templates_dir.mkdir(exist_ok=True)

    logger.info(f"Используется директория шаблонов: {templates_dir}")

    # Инициализируем шаблонизатор Jinja2 с настройкой рекурсивного поиска
    templates = Jinja2Templates(directory=str(templates_dir))

    # Настройка Jinja2 для поддержки рекурсивного поиска шаблонов
    templates.env.loader.searchpath = [str(templates_dir)]

    # Сохраняем путь для удобного доступа
    templates_path = str(templates_dir)

except Exception as e:
    logger.error(f"Ошибка при инициализации шаблонизатора: {e}")
    # Используем простой путь, если возникла ошибка
    templates_dir = Path("templates")
    if not templates_dir.exists():
        templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))
    templates_path = str(templates_dir)


def render_error_page(request, error_message, exception=None, status_code=500):
    """
    Отображает страницу ошибки с использованием шаблона 500.html

    Args:
        request: объект запроса FastAPI
        error_message: сообщение об ошибке для пользователя
        exception: объект исключения для логирования (опционально)
        status_code: HTTP-код ответа (по умолчанию 500)
    """
    if exception:
        logger.error(f"{error_message}: {exception}")

    return templates.TemplateResponse(
        "error/index.html",
        {"request": request, "error_message": error_message},
        status_code=status_code,
    )
