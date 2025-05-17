from fastapi import Request, status
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
from app.templates import templates
import logging

logger = logging.getLogger(__name__)


async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик ошибки 401 Unauthorized - срабатывает при попытке доступа
    к защищенным ресурсам без авторизации
    """
    logger.warning(f"Unauthorized access attempt: {request.url.path}")

    return HTMLResponse(
        content=templates.TemplateResponse(
            "errors/401.html", {"request": request}
        ).body,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик ошибки 404 Not Found - срабатывает при запросе несуществующих ресурсов
    """
    logger.info(f"Not found: {request.url.path}")

    return HTMLResponse(
        content=templates.TemplateResponse(
            "errors/404.html", {"request": request}
        ).body,
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Обработчик общих исключений - отображает дружественную страницу
    вместо стандартной ошибки сервера
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return HTMLResponse(
        content=templates.TemplateResponse(
            "errors/500.html", {"request": request}
        ).body,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
