from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.auth_utils import get_current_user, get_db
from app.password_utils import get_password_hash, verify_password
from app.models import User
from app.templates import templates
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

        # Иначе отображаем публичную страницу
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Ошибка при отображении главной страницы: {e}")
        # Возвращаем простой HTML в случае ошибки
        return HTMLResponse(
            content=f"""
        <html>
            <head><title>New Level - Сервис изучения английского</title></head>
            <body>
                <h1>Добро пожаловать в New Level!</h1>
                <p>Наш сервис временно работает в ограниченном режиме.</p>
                <p><a href="/login">Войти</a> | <a href="/register">Регистрация</a></p>
            </body>
        </html>
        """
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
        return HTMLResponse(
            content="<h1>Ошибка при загрузке профиля</h1><p>Попробуйте позже</p>"
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
    """
    Обновляет профиль пользователя.
    Требует аутентификацию.
    """
    errors = []

    # Если email изменился, проверить что новый email не занят другим пользователем
    if email != current_user.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            errors.append("Этот email уже используется другим аккаунтом")

    # Если введён новый пароль (не пустой) - проверяем требования
    new_password_hash = None
    if password:
        if len(password) < 4:
            errors.append("Новый пароль слишком короткий (минимум 4 символа)")
        else:
            new_password_hash = get_password_hash(password)

    if errors:
        # Вернуть страницу профиля с сообщениями об ошибках
        return templates.TemplateResponse(
            "profile.html", {"request": request, "user": current_user, "errors": errors}
        )

    try:
        # Обновляем данные пользователя
        current_user.name = name
        if email != current_user.email:
            current_user.email = email
        if new_password_hash:
            current_user.password_hash = new_password_hash

        db.commit()
        # Перенаправляем обратно на страницу профиля
        return RedirectResponse(url="/profile", status_code=303)
    except Exception as e:
        logger.error(f"Ошибка при обновлении профиля: {e}")
        errors.append("Ошибка при сохранении данных. Попробуйте позже.")
        return templates.TemplateResponse(
            "profile.html", {"request": request, "user": current_user, "errors": errors}
        )
