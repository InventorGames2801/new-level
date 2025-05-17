from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.auth_utils import get_current_user, get_db
from app.password_utils import get_password_hash, verify_password
from app.models import User
from app.templates import templates, render_error_page
import app.database as database
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    """
    Публичная домашняя страница, доступная без аутентификации.
    """
    try:
        user_id = request.session.get("user_id")

        # Если пользователь авторизован - показываем его профиль
        if user_id:
            try:
                db = next(get_db())
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return templates.TemplateResponse(
                        "index-log.html", {"request": request, "user": user}
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
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Ошибка при отображении главной страницы: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке главной страницы",
            exception=e
        )


@router.get("/profile", response_class=HTMLResponse)
def show_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Отображает профиль (форму редактирования) текущего пользователя.
    Требует аутентификацию.
    """
    try:
        # Получаем статистику пользователя
        stats = database.get_user_stats(db, current_user.id)

        # Рассчитываем прогресс до следующего уровня
        exp_for_level_up = database.get_game_setting_int(db, "points_for_level_up", 100)
        progress_percent = int((current_user.experience / exp_for_level_up) * 100)

        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats,
                "exp_for_level_up": exp_for_level_up,
                "progress_percent": progress_percent,
                "authenticated": True,
            },
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении профиля: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке профиля пользователя",
            exception=e
        )


@router.post("/profile")
def update_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
):
    try:
        # If email changed, check if new email is already taken
        if email != current_user.email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return RedirectResponse(
                    url="/profile?error=This email is already used by another account",
                    status_code=303,
                )

        # If new password entered, check requirements
        new_password_hash = None
        if password:
            if len(password) < 4:
                return RedirectResponse(
                    url="/profile?error=New password too short (minimum 4 characters)",
                    status_code=303,
                )
            else:
                new_password_hash = get_password_hash(password)

        # Update user data
        current_user.name = name
        if email != current_user.email:
            current_user.email = email
        if new_password_hash:
            current_user.password_hash = new_password_hash

        db.commit()

        # Redirect back to profile with success message
        return RedirectResponse(
            url="/profile?success=Profile updated successfully", status_code=303
        )
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        return render_error_page(
            request=request,
            error_message="Ошибка при обновлении профиля пользователя",
            exception=e
        )
