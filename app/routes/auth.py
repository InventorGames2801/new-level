from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.models import User
from app.auth_utils import get_db
from app.password_utils import get_password_hash, verify_password
from app.templates import templates, render_error_page
from datetime import datetime, timezone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    try:
        # Отображаем страницу с формой логина
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке страницы входа",
            exception=e
        )


@router.post("/login")
def process_login(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            # Invalid login - return login page with error
            return RedirectResponse(
                url="/login?error=Invalid email or password", status_code=303
            )

        # Update last_login when successful
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        # Save user_id and role in session
        request.session["user_id"] = user.id
        request.session["role"] = user.role

        # Redirect to home page after login with success message
        return RedirectResponse(
            url="/?success=You have successfully logged in", status_code=303
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке входа: {e}")
        db.rollback()
        return render_error_page(
            request=request,
            error_message="Ошибка при попытке входа в систему",
            exception=e
        )


@router.post("/register")
def process_register(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    try:
        # Check email
        if db.query(User).filter(User.email == email).first():
            return RedirectResponse(
                url="/register?error=Email already registered", status_code=303
            )

        # Basic password check
        if len(password) < 4:
            return RedirectResponse(
                url="/register?error=Password too short (minimum 4 characters)",
                status_code=303,
            )

        # Create new user
        hashed_pw = get_password_hash(password)
        new_user = User(name=name, email=email, password_hash=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Auto-login - save to session
        request.session["user_id"] = new_user.id
        request.session["role"] = new_user.role

        # Redirect to home with success message
        return RedirectResponse(
            url="/?success=Registration successful! Welcome to New Level", status_code=303
        )
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}")
        db.rollback()
        return render_error_page(
            request=request,
            error_message="Ошибка при регистрации пользователя",
            exception=e
        )


@router.get("/logout")
def logout(request: Request):
    try:
        # Очистка сессии и перенаправление на страницу логина
        request.session.clear()
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        logger.error(f"Ошибка при выходе из системы: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при выходе из системы",
            exception=e
        )


@router.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    try:
        # Отображаем страницу с формой регистрации
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке страницы регистрации",
            exception=e
        )
