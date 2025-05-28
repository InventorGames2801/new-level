from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query, Request, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from app.database import get_db, get_random_words
from app.models import User, UserWordHistory, Word
from app.auth_utils import get_current_user
from app.templates import templates, render_error_page
import app.database as database
import app.schemas as schemas
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/game", response_class=HTMLResponse)
def game_page(request: Request, current_user: User = Depends(get_current_user)):
    """
    Отображает страницу с игрой.
    Требует аутентификации.
    """
    try:
        db = next(get_db())
        # Получаем необходимые настройки игры
        settings = database.get_all_game_settings(db)

        # Получаем статистику пользователя
        stats = database.get_user_stats(db, current_user.id)

        # Рассчитываем прогресс до следующего уровня
        exp_for_level_up = database.get_game_setting_int(db, "points_for_level_up", 100)
        progress_percent = int((current_user.experience / exp_for_level_up) * 100)

        return templates.TemplateResponse(
            "game.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats,
                "settings": settings,
                "progress_percent": progress_percent,
                "exp_for_level_up": exp_for_level_up,
                "authenticated": True,
            },
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении страницы игры: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при загрузке игры. Пожалуйста, попробуйте позже.",
            exception=e,
        )


@router.post("/api/game/start")
def start_game_session(
    request: Request,
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Создает новую игровую сессию и возвращает ее ID.
    """
    try:
        game_type = data.get("game_type")

        if not game_type or game_type not in ["scramble", "matching", "typing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип игры"
            )

        session = database.create_game_session(db, current_user.id, game_type)

        return {"session_id": session.id, "game_type": game_type}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка при создании игровой сессии: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка при создании игровой сессии: {str(e)}"},
        )


@router.get("/api/words/{game_type}")
def get_game_words(
    game_type: str,
    request: Request,
    count: int = Query(5, gt=0, le=20),
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Проверяем, что тип игры допустимый
        if game_type not in ["scramble", "matching", "typing"]:
            raise HTTPException(status_code=400, detail="Invalid game type")

        # Получаем исключенные слова (использованные пользователем недавно)
        excluded_ids = (
            db.query(UserWordHistory.word_id)
            .filter(
                UserWordHistory.user_id == current_user.id,
                UserWordHistory.used_at
                > datetime.now(timezone.utc) - timedelta(hours=48),
            )
            .distinct()
            .all()
        )
        excluded_ids = [x[0] for x in excluded_ids]

        # Определяем сложность на основе уровня пользователя, если не указана
        if not difficulty:
            if current_user.level < 4:
                difficulty = "easy"
            elif current_user.level < 8:
                difficulty = "medium"
            else:
                difficulty = "hard"

        # Получаем случайные слова, исключая недавно использованные
        words = get_random_words(db, current_user.id, count, difficulty, excluded_ids)

        # Подготавливаем результат - НЕ отправляем правильные ответы
        result = []
        for word in words:
            # Базовая информация без правильных ответов
            word_data = {
                "id": word.id,
                "difficulty": word.difficulty,
            }

            # Информация в зависимости от типа игры
            if game_type == "scramble":
                # Для анаграмм даем только перемешанное слово и описание
                from app.game_utils import create_scrambled_word

                word_data["scrambled"] = create_scrambled_word(word.text)
                word_data["description"] = word.description

            elif game_type == "matching":
                # Для сопоставления даем английское слово и описание
                word_data["text"] = word.text
                word_data["description"] = word.description
                word_data["translation"] = word.translation

            elif game_type == "typing":
                # Для написания даем только описание
                word_data["description"] = word.description

            result.append(word_data)

        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка при получении слов для игры: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при получении слов для игры",
            exception=e,
        )


@router.post("/api/word/check")
def check_word_answer(
    request: Request,
    word_id: int = Body(...),
    answer: str = Body(...),
    game_type: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Проверяет ответ пользователя на слово.
    """
    try:
        word = db.query(Word).filter(Word.id == word_id).first()
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Слово не найдено"
            )

        # Нормализуем строки для сравнения: удаляем пробелы, приводим к нижнему регистру
        answer_clean = answer.lower().strip()

        # Проверка ответа зависит от типа игры - ВСЯ ВАЛИДАЦИЯ НА СЕРВЕРЕ
        correct = False

        if game_type == "scramble":
            # Для анаграмм проверяем соответствие английскому слову
            word_text_clean = word.text.lower().strip()
            correct = answer_clean == word_text_clean
        elif game_type == "matching":
            # Для сопоставления проверяем соответствие переводу
            translation_clean = word.translation.lower().strip()
            correct = answer_clean == translation_clean
        elif game_type == "typing":
            # Для набора текста проверяем соответствие английскому слову
            word_text_clean = word.text.lower().strip()
            correct = answer_clean == word_text_clean

        # Обновляем статистику слова
        database.update_word_stats(db, word_id, correct)

        # Добавляем запись в историю использования слов пользователем
        word_history = UserWordHistory(
            user_id=current_user.id,
            word_id=word_id,
            used_at=datetime.now(timezone.utc),
            correct=correct,
            game_type=game_type,
        )
        db.add(word_history)
        db.commit()

        return {"correct": correct}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка при проверке ответа: {e}")
        return render_error_page(
            request=request, error_message="Ошибка при проверке ответа", exception=e
        )


@router.post("/api/game/end")
def end_game_session(
    request: Request,
    session_id: int = Body(...),
    score: int = Body(...),
    correct_answers: int = Body(...),
    total_questions: int = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Завершает игровую сессию и обновляет прогресс пользователя.
    """
    try:
        # Завершаем игровую сессию
        session = database.complete_game_session(
            db, session_id, score, correct_answers, total_questions
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Игровая сессия не найдена",
            )

        # Добавляем опыт пользователю (N опыта за правильный ответ)
        points_per_answer = database.get_game_setting_int(db, "points_per_answer", 10)
        exp_points = correct_answers * points_per_answer

        # Бонус за серию правильных ответов
        if correct_answers == total_questions and total_questions > 0:
            streak_bonus = database.get_game_setting_int(db, "streak_bonus", 5)
            exp_points += streak_bonus

        # Обновляем опыт пользователя и проверяем повышение уровня
        user, level_up, daily_limit_reached = database.add_user_experience(
            db, current_user.id, exp_points
        )

        # Получаем дневной лимит опыта и текущий прогресс
        daily_exp_limit = database.get_game_setting_int(
            db, "daily_experience_limit", 200
        )
        daily_exp_current = (
            user.daily_experience if hasattr(user, "daily_experience") else 0
        )

        # Формируем ответ
        result = {
            "experience_gained": 0 if daily_limit_reached else exp_points,
            "total_experience": user.experience,
            "level": user.level,
            "level_up": level_up,
            "daily_limit_reached": daily_limit_reached,
            "daily_exp_limit": daily_exp_limit,
            "daily_exp_current": daily_exp_current,
        }

        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка при завершении игровой сессии: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при завершении игровой сессии",
            exception=e,
        )


@router.get("/api/translation-options")
def get_translation_options(
    request: Request,
    count: int = Query(3, gt=0, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Возвращает варианты перевода для игры "Сопоставление".
    """
    try:
        # Получаем случайные слова
        words = db.query(Word).order_by(func.random()).limit(count).all()

        # Формируем варианты ответов (только переводы)
        options = []
        for word in words:
            options.append({"text": word.translation})

        return options
    except Exception as e:
        logger.error(f"Ошибка при получении вариантов перевода: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Ошибка при получении вариантов перевода"},
        )


@router.post("/api/matching/check")
def check_matching_answers(
    request: Request,
    answers: List[Dict[str, Any]] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Проверяет ответы для игры "Сопоставление".
    """
    try:
        results = []
        all_correct = True

        for answer in answers:
            word_id = answer.get("wordId")
            user_answer = answer.get("answer")

            if not word_id or not user_answer:
                continue

            # Получаем слово
            word = db.query(Word).filter(Word.id == word_id).first()
            if not word:
                continue

            # Проверяем ответ
            correct = word.translation.lower().strip() == user_answer.lower().strip()

            # Если хотя бы один ответ неверный, all_correct будет False
            if not correct:
                all_correct = False

            # Обновляем статистику слова
            database.update_word_stats(db, word_id, correct)

            # Добавляем запись в историю использования слов пользователем
            word_history = UserWordHistory(
                user_id=current_user.id,
                word_id=word_id,
                used_at=datetime.now(timezone.utc),
                correct=correct,
                game_type="matching",
            )
            db.add(word_history)

            # Добавляем результат (без правильных ответов)
            results.append({"word_id": word_id, "correct": correct})

        db.commit()

        return {"all_correct": all_correct, "results": results}
    except Exception as e:
        logger.error(f"Ошибка при проверке сопоставлений: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "Ошибка при проверке сопоставлений"}
        )


@router.get("/api/debug/word-count")
def get_word_count(request: Request, db: Session = Depends(get_db)):
    try:
        count = db.query(func.count(Word.id)).scalar()
        return {"count": count}
    except Exception as e:
        logger.error(f"Ошибка при подсчете количества слов: {e}")
        return render_error_page(
            request=request,
            error_message="Ошибка при получении статистики слов",
            exception=e,
        )
