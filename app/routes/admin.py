from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import random
import logging

from app.database import get_users_statistics, get_words_statistics
from app.models import User, Word, GameSetting, GameSession
from app.auth_utils import get_admin_user, get_db
from app.templates import templates, render_error_page

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
    try:
        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} просматривает панель администратора",
        )

        # Получаем расширенную статистику
        user_stats = get_users_statistics(db)
        words_stats = get_words_statistics(db)

        # Получаем общие настройки игры
        settings = db.query(GameSetting).all()

        return templates.TemplateResponse(
            "admin/index.html",
            {
                "request": request,
                "admin_user": current_admin,
                "user_stats": user_stats,
                "words_stats": words_stats,
                "settings": settings,
                "active_tab": "stats",
            },
        )
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке панели администратора",
            exception=e
        )


@router.get("/admin/dictionary", response_class=HTMLResponse)
def admin_dictionary(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
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
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке словаря",
            exception=e
        )


@router.get("/admin/settings", response_class=HTMLResponse)
def admin_settings(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
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
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке настроек",
            exception=e
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
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    text: str = Form(...),
    translation: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form(...),
):
    try:
        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} создает новое слово: {text}, сложность: {difficulty}",
        )

        # Валидация входных данных
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Текст слова не может быть пустым")

        if not translation or len(translation.strip()) == 0:
            raise HTTPException(status_code=400, detail="Перевод не может быть пустым")

        if not description or len(description.strip()) == 0:
            raise HTTPException(status_code=400, detail="Описание не может быть пустым")

        if difficulty not in ["easy", "medium", "hard"]:
            raise HTTPException(status_code=400, detail="Неверная сложность")

        # Создаем слово с унифицированной структурой
        try:
            word = Word(
                text=text.strip(),
                translation=translation.strip(),
                description=description.strip(),
                difficulty=difficulty,
                created_at=datetime.now(timezone.utc),
            )

            db.add(word)
            db.commit()

            logger.info(admin_log_format, f"Слово '{text}' успешно создано с ID: {word.id}")

            return RedirectResponse(url="/admin/dictionary", status_code=303)
        except Exception as e:
            db.rollback()
            logger.error(admin_log_format, f"Ошибка при создании слова: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при создании слова: {e}")
    except HTTPException as he:
        raise he
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при создании слова",
            exception=e
        )


@router.post("/admin/words/{word_id}/edit")
def update_word(
    word_id: int,
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    text: str = Form(...),
    translation: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form(...),
):
    try:
        # Проверяем существование слова
        word = db.query(Word).filter(Word.id == word_id).first()
        if not word:
            raise HTTPException(status_code=404, detail="Слово не найдено")

        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} обновляет слово ID: {word_id} с '{word.text}' на '{text}'",
        )

        # Валидация входных данных
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400, detail="Текст слова не может быть пустым"
            )

        if not translation or len(translation.strip()) == 0:
            raise HTTPException(status_code=400, detail="Перевод не может быть пустым")

        if not description or len(description.strip()) == 0:
            raise HTTPException(status_code=400, detail="Описание не может быть пустым")

        if difficulty not in ["easy", "medium", "hard"]:
            raise HTTPException(status_code=400, detail="Неверная сложность")

        # Обновляем данные слова
        word.text = text.strip()
        word.translation = translation.strip()
        word.description = description.strip()
        word.difficulty = difficulty

        db.commit()

        logger.info(admin_log_format, f"Слово ID: {word_id} успешно обновлено")

        return RedirectResponse(url="/admin/dictionary", status_code=303)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при обновлении слова: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при обновлении слова",
            exception=e
        )


@router.post("/admin/words/{word_id}/delete")
def delete_word(
    word_id: int,
    request: Request,
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
        return render_error_page(
            request=request,
            error_message="Ошибка при удалении слова",
            exception=e
        )


@router.get("/admin/words/{word_id}/edit", response_class=HTMLResponse)
def edit_word_form(
    word_id: int,
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
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
    except HTTPException as he:
        raise he
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке формы редактирования",
            exception=e
        )


@router.post("/admin/settings/update")
async def update_settings(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        logger.info(
            admin_log_format,
            f"Администратор {current_admin.email} обновляет настройки приложения",
        )

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
        return render_error_page(
            request=request,
            error_message="Ошибка при обновлении настроек",
            exception=e
        )


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    page: int = Query(1, ge=1),  # FastAPI Query, а не sqlalchemy.orm.Query
    per_page: int = Query(10, ge=5, le=100),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
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
    except Exception as e:
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке списка пользователей",
            exception=e
        )


@router.post("/admin/users/create")
def create_user(
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    try:
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
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Ошибка при создании пользователя: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при создании пользователя",
            exception=e
        )


@router.post("/admin/users/{user_id}/delete")
def delete_user(
    user_id: int,
    request: Request,
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
        return render_error_page(
            request=request,
            error_message="Ошибка при удалении пользователя",
            exception=e
        )


@router.post("/admin/users/{user_id}/toggle_admin_role")
def toggle_admin_view(
    user_id: int,
    request: Request,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(
            admin_log_format,
            f"Administrator {current_admin.email} is changing role for user {user.email} (ID: {user_id})",
        )

        # If we're trying to remove admin rights
        if user.role == "admin" and user.id != current_admin.id:
            # Check how many admins are in the system
            admin_count = db.query(User).filter(User.role == "admin").count()
            if admin_count <= 1:
                logger.warning(
                    admin_log_format,
                    "Attempt to remove rights from the last system administrator",
                )
                return RedirectResponse(
                    url="/admin/users?error=Cannot remove the last administrator from the system",
                    status_code=303,
                )

        # Prevent changing your own role
        if user.id == current_admin.id:
            logger.warning(
                admin_log_format,
                f"Administrator {current_admin.email} attempts to change their own role",
            )
            return RedirectResponse(
                url="/admin/users?error=You cannot change your own administrator role",
                status_code=303,
            )

        # Toggle role
        new_role = "user" if user.role == "admin" else "admin"
        user.role = new_role

        db.commit()

        logger.info(
            admin_log_format,
            f"User {user.email} (ID: {user_id}) role changed to '{new_role}'",
        )

        return RedirectResponse(
            url="/admin/users?success=User role successfully updated", status_code=303
        )
    except HTTPException as he:
        # Redirect with error message instead of raising the exception
        return RedirectResponse(url=f"/admin/users?error={he.detail}", status_code=303)
    except Exception as e:
        db.rollback()
        logger.error(admin_log_format, f"Error while changing user role: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при изменении роли пользователя",
            exception=e
        )
