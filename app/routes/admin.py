from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.models import User, Word, GameSetting, GameSession
from app.auth_utils import get_admin_user, get_db
from app.templates import templates
from sqlalchemy import func, distinct, and_
import random
import string

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    # Получаем данные для админ-панели
    users = db.query(User).all()
    words = db.query(Word).all()
    settings = db.query(GameSetting).all()

    # Считаем количество сыгранных игр
    games_count = db.query(func.count(GameSession.id)).scalar() or 0

    # Собираем статистику по словам
    words_stats = {
        "scramble": {
            "easy": db.query(func.count(Word.id))
            .filter(Word.game_type == "scramble", Word.difficulty == "easy")
            .scalar()
            or 0,
            "medium": db.query(func.count(Word.id))
            .filter(Word.game_type == "scramble", Word.difficulty == "medium")
            .scalar()
            or 0,
            "hard": db.query(func.count(Word.id))
            .filter(Word.game_type == "scramble", Word.difficulty == "hard")
            .scalar()
            or 0,
            "total": db.query(func.count(Word.id))
            .filter(Word.game_type == "scramble")
            .scalar()
            or 0,
        },
        "matching": {
            "easy": db.query(func.count(Word.id))
            .filter(Word.game_type == "matching", Word.difficulty == "easy")
            .scalar()
            or 0,
            "medium": db.query(func.count(Word.id))
            .filter(Word.game_type == "matching", Word.difficulty == "medium")
            .scalar()
            or 0,
            "hard": db.query(func.count(Word.id))
            .filter(Word.game_type == "matching", Word.difficulty == "hard")
            .scalar()
            or 0,
            "total": db.query(func.count(Word.id))
            .filter(Word.game_type == "matching")
            .scalar()
            or 0,
        },
        "typing": {
            "easy": db.query(func.count(Word.id))
            .filter(Word.game_type == "typing", Word.difficulty == "easy")
            .scalar()
            or 0,
            "medium": db.query(func.count(Word.id))
            .filter(Word.game_type == "typing", Word.difficulty == "medium")
            .scalar()
            or 0,
            "hard": db.query(func.count(Word.id))
            .filter(Word.game_type == "typing", Word.difficulty == "hard")
            .scalar()
            or 0,
            "total": db.query(func.count(Word.id))
            .filter(Word.game_type == "typing")
            .scalar()
            or 0,
        },
    }

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "admin_user": current_admin,
            "users": users,
            "words": words,
            "settings": settings,
            "games_count": games_count,
            "words_stats": words_stats,
        },
    )


@router.post("/admin/users/{user_id}/delete")
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    # Удаление пользователя (доступно только админу)
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# Функция для перемешивания букв в слове (для анаграмм)
def create_scrambled_word(word):
    chars = list(word)
    random.shuffle(chars)
    scrambled = "".join(chars).upper()

    # Если случайно получилось исходное слово - перемешиваем еще раз
    if scrambled.lower() == word.lower():
        return create_scrambled_word(word)

    return scrambled


@router.post("/admin/words/create")
def create_word(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    text: str = Form(...),
    game_type: str = Form(...),
    difficulty: str = Form(...),
    scrambled: str = Form(None),
    translation: str = Form(None),
    description: str = Form(None),
):
    # Создаем новое слово
    word = Word(text=text, game_type=game_type, difficulty=difficulty)

    # Добавляем специфические поля в зависимости от типа игры
    if game_type == "scramble":
        word.scrambled = scrambled if scrambled else create_scrambled_word(text)
    elif game_type == "matching":
        word.translation = translation
    elif game_type == "typing":
        word.description = description

    db.add(word)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/words/{word_id}/delete")
def delete_word(
    word_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    # Удаление слова
    db.query(Word).filter(Word.id == word_id).delete()
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@router.get("/admin/words/{word_id}/edit", response_class=HTMLResponse)
def edit_word_form(
    word_id: int,
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    # Получаем слово для редактирования
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")

    return templates.TemplateResponse(
        "edit_word.html",
        {"request": request, "admin_user": current_admin, "word": word},
    )


@router.post("/admin/words/{word_id}/edit")
def update_word(
    word_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    text: str = Form(...),
    game_type: str = Form(...),
    difficulty: str = Form(...),
    scrambled: str = Form(None),
    translation: str = Form(None),
    description: str = Form(None),
):
    # Обновляем существующее слово
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Слово не найдено")

    word.text = text
    word.game_type = game_type
    word.difficulty = difficulty

    # Обновляем специфические поля в зависимости от типа игры
    if game_type == "scramble":
        word.scrambled = scrambled if scrambled else create_scrambled_word(text)
        word.translation = None
        word.description = None
    elif game_type == "matching":
        word.translation = translation
        word.scrambled = None
        word.description = None
    elif game_type == "typing":
        word.description = description
        word.scrambled = None
        word.translation = None

    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/settings/update")
async def update_settings(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    # Обновляем настройки игры
    form_data = await request.form()

    # Обрабатываем все существующие настройки
    for key, value in form_data.items():
        if key.startswith("setting_"):
            setting_key = key.replace("setting_", "")
            setting = (
                db.query(GameSetting).filter(GameSetting.key == setting_key).first()
            )
            if setting:
                setting.value = value

    # Добавляем новую настройку, если указаны оба поля
    new_key = form_data.get("new_key")
    new_value = form_data.get("new_value")
    if new_key and new_value:
        # Проверяем, не существует ли уже такая настройка
        existing = db.query(GameSetting).filter(GameSetting.key == new_key).first()
        if not existing:
            new_setting = GameSetting(key=new_key, value=new_value)
            db.add(new_setting)

    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/users/create")
def create_user(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    # Проверяем, не существует ли уже пользователь с таким email
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        )

    # Создаем нового пользователя
    from app.password_utils import get_password_hash

    user = User(
        name=name, email=email, password_hash=get_password_hash(password), role=role
    )

    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/users/{user_id}/toggle_admin")
def toggle_admin_view(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Переключение роли
    user.role = "user" if user.role == "admin" else "admin"
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)
