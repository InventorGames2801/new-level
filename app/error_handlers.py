from fastapi import Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from app.templates import templates
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик HTTP-исключений, учитывающий тип запроса (API или веб-страница)
    """
    # Для API-запросов возвращаем JSON с ошибкой
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # Для страниц административной панели перенаправляем с сообщением об ошибке
    if request.url.path.startswith("/admin"):
        return RedirectResponse(url=f"/admin?error={exc.detail}", status_code=303)

    # Для обычных веб-страниц показываем шаблон с ошибкой
    error_type = "error"
    title = "Ошибка"

    if exc.status_code == 401:
        template = "error/401.html"
        title = "Требуется авторизация"
    elif exc.status_code == 403:
        template = "error/403.html"
        title = "Доступ запрещен"
    elif exc.status_code == 404:
        template = "error/404.html"
        title = "Страница не найдена"
    else:
        template = "error/500.html"
        title = "Ошибка сервера"

    # Если пользователь запрашивает через popup, перенаправляем с ошибкой в URL
    use_popup = request.query_params.get("use_popup") == "true"
    if use_popup:
        return RedirectResponse(
            url=f"/{request.query_params.get('redirect_to', '')}?error={exc.detail}",
            status_code=303,
        )

    return HTMLResponse(
        content=templates.TemplateResponse(
            template, {"request": request, "error": exc.detail, "title": title}
        ).body,
        status_code=exc.status_code,
    )


async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик ошибки 401 Unauthorized - срабатывает при попытке доступа
    к защищенным ресурсам без авторизации
    """
    logger.warning(f"Unauthorized access attempt: {request.url.path}")

    return HTMLResponse(
        content=templates.TemplateResponse("error/401.html", {"request": request}).body,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик ошибки 404 Not Found - срабатывает при запросе несуществующих ресурсов
    """
    logger.info(f"Not found: {request.url.path}")

    return HTMLResponse(
        content=templates.TemplateResponse("error/404.html", {"request": request}).body,
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Обработчик общих исключений - отображает дружественную страницу
    вместо стандартной ошибки сервера
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return HTMLResponse(
        content=templates.TemplateResponse("error/500.html", {"request": request}).body,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
