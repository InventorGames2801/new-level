# routes/user.py
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.auth_utils import get_current_user, get_db, get_password_hash, verify_password
from app.models import User

from main import templates

router = APIRouter()

@router.get("/")
def index_page(request: Request, current_user: User = Depends(get_current_user)):
    # Главная страница для авторизованного пользователя
    return templates.TemplateResponse("index-log.html", {"request": request, "user": current_user})

@router.get("/profile")
def show_profile(request: Request, current_user: User = Depends(get_current_user)):
    # Отображаем профиль (форму редактирования) текущего пользователя
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@router.post("/profile")
def update_profile(request: Request, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db),
                   name: str = Form(...), email: str = Form(...), password: str = Form(None)):
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
            errors.append("Новый пароль слишком короткий")
        else:
            new_password_hash = get_password_hash(password)
    if errors:
        # Вернуть страницу профиля с сообщениями об ошибках
        return templates.TemplateResponse("profile.html", {
            "request": request, "user": current_user, "errors": errors
        })
    # Обновляем данные пользователя
    current_user.name = name
    if email != current_user.email:
        current_user.email = email
    if new_password_hash:
        current_user.password_hash = new_password_hash
    db.commit()
    # Опционально, можно добавить сообщение о успехе через flash-сообщения
    return RedirectResponse(url="/profile", status_code=303)
