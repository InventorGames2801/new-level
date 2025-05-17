from fastapi import APIRouter, Request, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User
from app.auth_utils import get_current_user
from app.templates import templates
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
        return HTMLResponse(
            content="<h1>Ошибка при загрузке игры</h1><p>Попробуйте позже</p>"
        )


@router.post("/api/game/start")
def start_game_session(
    game_type: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Создает новую игровую сессию и возвращает ее ID.
    """
    try:
        if game_type not in ["scramble", "matching", "typing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип игры"
            )

        session = database.create_game_session(db, current_user.id, game_type)

        return {"session_id": session.id, "game_type": game_type}
    except Exception as e:
        logger.error(f"Ошибка при создании игровой сессии: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании игровой сессии",
        )


@router.post("/api/game/end")
def end_game_session(
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

        # Добавляем опыт пользователю (1 опыт за правильный ответ)
        points_per_answer = database.get_game_setting_int(db, "points_per_answer", 10)
        exp_points = correct_answers * points_per_answer

        # Бонус за серию правильных ответов
        if correct_answers == total_questions and total_questions > 0:
            streak_bonus = database.get_game_setting_int(db, "streak_bonus", 5)
            exp_points += streak_bonus

        # Обновляем опыт пользователя и проверяем повышение уровня
        user, level_up = database.add_user_experience(db, current_user.id, exp_points)

        # Формируем ответ
        result = {
            "experience_gained": exp_points,
            "total_experience": user.experience,
            "level": user.level,
            "level_up": level_up,
        }

        return result
    except Exception as e:
        logger.error(f"Ошибка при завершении игровой сессии: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при завершении игровой сессии",
        )


@router.get("/api/words/{game_type}")
def get_words_for_game(
    game_type: str,
    count: int = 5,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Возвращает случайные слова для игры.
    """
    try:
        if game_type not in ["scramble", "matching", "typing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный тип игры"
            )

        # Если не указана сложность, выбираем в зависимости от уровня пользователя
        if not difficulty:
            # Простая логика: уровни 1-3 - easy, 4-7 - medium, 8+ - hard
            if current_user.level < 4:
                difficulty = "easy"
            elif current_user.level < 8:
                difficulty = "medium"
            else:
                difficulty = "hard"

        words = database.get_random_words(db, game_type, count, difficulty)

        # Преобразуем в формат, подходящий для игры
        result = []
        for word in words:
            word_data = {"id": word.id, "difficulty": word.difficulty}

            if game_type == "scramble":
                word_data["text"] = word.text
                word_data["scrambled"] = word.scrambled
            elif game_type == "matching":
                word_data["text"] = word.text
                word_data["translation"] = word.translation
            elif game_type == "typing":
                word_data["text"] = word.text
                word_data["description"] = word.description

            result.append(word_data)

        return result
    except Exception as e:
        logger.error(f"Ошибка при получении слов для игры: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении слов для игры",
        )


@router.post("/api/word/check")
def check_word_answer(
    word_id: int = Body(...),
    answer: str = Body(...),
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

        # Проверяем ответ в зависимости от типа игры
        correct = False
        if word.game_type == "scramble" or word.game_type == "typing":
            correct = answer.lower().strip() == word.text.lower().strip()
        elif word.game_type == "matching":
            correct = answer.lower().strip() == word.translation.lower().strip()

        # Обновляем статистику слова
        database.update_word_stats(db, word_id, correct)

        return {"correct": correct}
    except Exception as e:
        logger.error(f"Ошибка при проверке ответа: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проверке ответа",
        )
