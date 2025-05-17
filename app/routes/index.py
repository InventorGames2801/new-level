from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.auth_utils import get_optional_user
from app.templates import templates, render_error_page
import app.database as crud
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request, db: Session = Depends(get_db)):
    """
    Главная страница сайта.
    Отображает разное содержимое в зависимости от авторизации пользователя.
    """
    try:
        user_id = request.session.get("user_id")

        # Если пользователь авторизован - показываем его личный кабинет
        if user_id:
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Получаем статистику пользователя
                    stats = crud.get_user_stats(db, user.id)

                    # Рассчитываем прогресс до следующего уровня
                    exp_for_level_up = crud.get_game_setting_int(
                        db, "points_for_level_up", 100
                    )
                    progress_percent = int((user.experience / exp_for_level_up) * 100)

                    return templates.TemplateResponse(
                        "index.html",
                        {
                            "request": request,
                            "user": user,
                            "stats": stats,
                            "progress_percent": progress_percent,
                            "exp_for_level_up": exp_for_level_up,
                            "authenticated": True,
                        },
                    )
            except Exception as e:
                logger.error(f"Ошибка при получении пользователя: {e}")
                # Если ошибка с БД, очищаем сессию, чтобы пользователь не был "заперт"
                request.session.clear()
                return render_error_page(
                    request=request,
                    error_message="Ошибка при получении данных пользователя",
                    exception=e
                )

        # Иначе отображаем публичную страницу
        return templates.TemplateResponse(
            "index.html", {"request": request, "authenticated": False}
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении главной страницы: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке главной страницы",
            exception=e
        )


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """
    Страница о проекте
    """
    try:
        authenticated = user is not None

        return templates.TemplateResponse(
            "about.html", {"request": request, "authenticated": authenticated, "user": user}
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении страницы о проекте: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке страницы о проекте",
            exception=e
        )


@router.get("/training", response_class=HTMLResponse)
def training_page(request: Request, user: Optional[User] = Depends(get_optional_user)):
    """
    Страница о методике обучения
    """
    try:
        authenticated = user is not None

        return templates.TemplateResponse(
            "training.html",
            {"request": request, "authenticated": authenticated, "user": user},
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении страницы обучения: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке страницы с информацией об обучении",
            exception=e
        )
