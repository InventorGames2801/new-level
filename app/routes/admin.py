from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.models import User, Word, GameSetting, GameSession
from app.auth_utils import get_admin_user, get_db
from app.templates import templates
from sqlalchemy import func
import random
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Настраиваем форматирование для выделения админских логов
admin_log_format = "🔐 [ADMIN ACTION] %s"


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} просматривает панель администратора",
    )

    users = db.query(User).all()
    words = db.query(Word).all()
    settings = db.query(GameSetting).all()
    games_count = db.query(func.count(GameSession.id)).scalar() or 0

    words_stats = {
        "scramble": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
        "matching": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
        "typing": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
    }

    for word in words:
        if word.game_type in words_stats:
            words_stats[word.game_type][word.difficulty] += 1
            words_stats[word.game_type]["total"] += 1

    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "admin_user": current_admin,
            "users": users,
            "words": words,
            "settings": settings,
            "games_count": games_count,
            "words_stats": words_stats,
            "active_tab": "stats",
        },
    )


@router.get("/admin/dictionary", response_class=HTMLResponse)
def admin_dictionary(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format, f"Администратор {current_admin.email} просматривает словарь"
    )

    words = db.query(Word).all()

    # TODO: Добавить фильтрацию и сортировку слов

    return templates.TemplateResponse(
        "admin/dictionary.html",
        {
            "request": request,
            "admin_user": current_admin,
            "words": words,
            "active_tab": "dictionary",
        },
    )


@router.get("/admin/settings", response_class=HTMLResponse)
def admin_settings(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format, f"Администратор {current_admin.email} просматривает настройки"
    )

    settings = db.query(GameSetting).all()

    # TODO: Добавить категоризацию настроек

    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "admin_user": current_admin,
            "settings": settings,
            "active_tab": "settings",
        },
    )


# Служебная функция для создания анаграмм с рекурсивной защитой от совпадений
def create_scrambled_word(word):
    chars = list(word)
    random.shuffle(chars)
    scrambled = "".join(chars).upper()

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
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} создает новое слово: {text} (тип: {game_type}, сложность: {difficulty})",
    )

    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Текст слова не может быть пустым")

    if game_type not in ["scramble", "matching", "typing"]:
        raise HTTPException(status_code=400, detail="Неверный тип игры")

    if difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Неверная сложность")

    if game_type == "matching" and (not translation or len(translation.strip()) == 0):
        raise HTTPException(
            status_code=400, detail="Для типа 'matching' требуется перевод"
        )

    if game_type == "typing" and (not description or len(description.strip()) == 0):
        raise HTTPException(
            status_code=400, detail="Для типа 'typing' требуется описание"
        )

    try:
        word = Word(text=text, game_type=game_type, difficulty=difficulty)

        # Разное поведение для разных типов игр - только одно поле заполняется, остальные очищаются
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

        db.add(word)
        db.commit()

        logger.info(admin_log_format, f"Слово '{text}' успешно создано с ID: {word.id}")

        return RedirectResponse(url="/admin/dictionary", status_code=303)
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при создании слова: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании слова: {e}")


@router.post("/admin/words/{word_id}/delete")
def delete_word(
    word_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        word = db.query(Word).filter(Word.id == word_id).first()
        if not word:
            raise HTTPException(status_code=404, detail="Слово не найдено")

        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} удаляет слово ID: {word_id}, текст: '{word.text}'",
        )

        db.delete(word)
        db.commit()

        logger.info(admin_log_format, f"Слово с ID: {word_id} успешно удалено")

        return RedirectResponse(url="/admin/dictionary", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при удалении слова: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении слова: {e}")


@router.get("/admin/words/{word_id}/edit", response_class=HTMLResponse)
def edit_word_form(
    word_id: int,
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} открывает форму редактирования слова ID: {word_id}",
    )

    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        logger.warning(
            admin_log_format,
            f"Попытка редактирования несуществующего слова ID: {word_id}",
        )
        raise HTTPException(status_code=404, detail="Слово не найдено")

    return templates.TemplateResponse(
        "admin/edit_word.html",
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
    """
    Обновляет существующее слово с валидацией и обработкой ошибок.
    """
    try:
        word = db.query(Word).filter(Word.id == word_id).first()
        if not word:
            raise HTTPException(status_code=404, detail="Слово не найдено")

        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} обновляет слово ID: {word_id} с '{word.text}' на '{text}'",
        )

        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400, detail="Текст слова не может быть пустым"
            )

        if game_type not in ["scramble", "matching", "typing"]:
            raise HTTPException(status_code=400, detail="Неверный тип игры")

        if difficulty not in ["easy", "medium", "hard"]:
            raise HTTPException(status_code=400, detail="Неверная сложность")

        if game_type == "matching" and (
            not translation or len(translation.strip()) == 0
        ):
            raise HTTPException(
                status_code=400, detail="Для типа 'matching' требуется перевод"
            )

        if game_type == "typing" and (not description or len(description.strip()) == 0):
            raise HTTPException(
                status_code=400, detail="Для типа 'typing' требуется описание"
            )

        word.text = text
        word.game_type = game_type
        word.difficulty = difficulty

        # Взаимоисключающие поля в зависимости от типа игры
        if game_type == "scramble":
            if not scrambled or len(scrambled.strip()) == 0:
                word.scrambled = create_scrambled_word(text)
            else:
                word.scrambled = scrambled
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

        logger.info(admin_log_format, f"Слово ID: {word_id} успешно обновлено")

        return RedirectResponse(url="/admin/dictionary", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при обновлении слова: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении слова: {e}")


@router.post("/admin/settings/update")
async def update_settings(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} обновляет настройки приложения",
    )

    try:
        form_data = await request.form()
        updated_keys = []

        for key, value in form_data.items():
            if key.startswith("setting_"):
                setting_key = key.replace("setting_", "")

                if value is None or len(str(value).strip()) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Значение для настройки '{setting_key}' не может быть пустым",
                    )

                setting = (
                    db.query(GameSetting).filter(GameSetting.key == setting_key).first()
                )
                if setting:
                    # Логируем только если значение изменилось
                    if setting.value != value:
                        logger.info(
                            admin_log_format,
                            f"Настройка '{setting_key}' изменена с '{setting.value}' на '{value}'",
                        )
                        setting.value = value
                        updated_keys.append(setting_key)

        db.commit()

        # Финальный лог для общего результата операции
        if updated_keys:
            logger.info(
                admin_log_format, f"Обновлены настройки: {', '.join(updated_keys)}"
            )
        else:
            logger.info(
                admin_log_format, "Настройки проверены, но изменений не внесено"
            )

        return RedirectResponse(url="/admin/settings", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при обновлении настроек: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка при обновлении настроек: {e}"
        )


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    page: int = Query(1, ge=1),  # FastAPI Query, а не sqlalchemy.orm.Query
    per_page: int = Query(10, ge=5, le=100),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} просматривает список пользователей (страница {page})",
    )

    total_users = db.query(func.count(User.id)).scalar()
    total_pages = (total_users + per_page - 1) // per_page

    # TODO: добавить фильтрацию и поиск по имени/email

    users = (
        db.query(User)
        .order_by(User.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "admin_user": current_admin,
            "users": users,
            "active_tab": "users",
            "current_page": page,
            "total_pages": total_pages,
            "per_page": per_page,
        },
    )


@router.post("/admin/users/create")
def create_user(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    logger.info(
        admin_log_format,
        f"Администратор {current_admin.email} создает нового пользователя с email: {email}, роль: {role}",
    )

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.warning(
            admin_log_format,
            f"Попытка создания пользователя с существующим email: {email}",
        )
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        )

    try:
        from app.password_utils import get_password_hash

        user = User(
            name=name, email=email, password_hash=get_password_hash(password), role=role
        )

        db.add(user)
        db.commit()

        logger.info(
            admin_log_format,
            f"Пользователь с email {email} успешно создан с ID: {user.id}",
        )

        return RedirectResponse(url="/admin/users", status_code=303)
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при создании пользователя: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка при создании пользователя: {e}"
        )


@router.post("/admin/users/{user_id}/delete")
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        if user_id == current_admin.id:
            logger.warning(
                admin_log_format,
                f"Администратор {current_admin.email} пытается удалить свою собственную учетную запись",
            )
            raise HTTPException(
                status_code=400,
                detail="Невозможно удалить свою собственную учетную запись администратора",
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} удаляет пользователя {user.email} (ID: {user_id})",
        )

        db.delete(user)
        db.commit()

        logger.info(admin_log_format, f"Пользователь с ID: {user_id} успешно удален")

        return RedirectResponse(url="/admin/users", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при удалении пользователя: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении пользователя: {e}"
        )


@router.post("/admin/users/{user_id}/toggle_admin_role")
def toggle_admin_view(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} меняет роль пользователя {user.email} (ID: {user_id})",
        )

        # Критичная проверка - предотвращаем снятие последнего администратора
        if user.role == "admin" and user.id != current_admin.id:
            admin_count = db.query(User).filter(User.role == "admin").count()
            if admin_count <= 1:
                logger.warning(
                    admin_log_format,
                    "Попытка снять права с последнего администратора системы",
                )
                raise HTTPException(
                    status_code=400,
                    detail="Невозможно снять права с последнего администратора системы",
                )

        # Нельзя менять свою собственную роль - это может привести к потере доступа
        if user.id == current_admin.id:
            logger.warning(
                admin_log_format,
                f"Администратор {current_admin.email} пытается изменить собственную роль",
            )
            raise HTTPException(
                status_code=400,
                detail="Невозможно изменить собственную роль администратора",
            )

        new_role = "user" if user.role == "admin" else "admin"
        user.role = new_role

        db.commit()

        logger.info(
            admin_log_format,
            f"Роль пользователя {user.email} (ID: {user_id}) изменена на '{new_role}'",
        )

        return RedirectResponse(url="/admin/users", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при изменении роли пользователя: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при изменении роли: {e}")
