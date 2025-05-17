from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.models import User
from app.auth_utils import get_db
from app.password_utils import get_password_hash, verify_password
from app.templates import templates
from datetime import datetime, timezone

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    # Отображаем страницу с формой логина
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def process_login(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        # Неверный логин или пароль: возвращаем страницу логина с сообщением об ошибке
        error_msg = "Неправильный email или пароль"
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": error_msg, "email": email}
        )

    # Добавляем: обновляем last_login при успешном входе
    user.last_login = datetime.now(timezone.utc)
    db.commit()  # Сохраняем изменения в БД

    # Успешный вход: сохраняем user_id и роль в сессию
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    # Редирект на главную страницу после входа
    return RedirectResponse(url="/", status_code=303)


@router.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    # Отображаем страницу с формой регистрации
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def process_register(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    errors = []
    # Проверка email
    if db.query(User).filter(User.email == email).first():
        errors.append("Email уже зарегистрирован")
    # Примитивная проверка пароля (например, длина не меньше 4)
    if len(password) < 4:
        errors.append("Пароль слишком короткий (минимум 4 символа)")
    if errors:
        # Есть ошибки - возвращаем форму с сообщениями
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "errors": errors, "name": name, "email": email},
        )
    # Создание нового пользователя
    hashed_pw = get_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # получаем сгенерированный id
    # Автовход нового пользователя: сохраняем в сессию
    request.session["user_id"] = new_user.id
    request.session["role"] = new_user.role
    # Редирект на главную страницу вошедшего пользователя
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    # Очистка сессии и перенаправление на страницу логина
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
