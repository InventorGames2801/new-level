"""
Refactored game routes following SOLID principles
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.auth_utils import get_current_user
from app.models import User
from app.database import get_db
from ..services.game_service import GameService
from ..services.user_service import UserService
from ..repositories.base_repository import SQLAlchemyRepository
from ..exceptions import GameValidationError, WordNotFoundError, AppException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_game_service(db: Session = Depends(get_db)) -> GameService:
    """Dependency injection for GameService"""
    from app.models import Word, GameSession, UserWordHistory
    
    word_repo = SQLAlchemyRepository(db, Word)
    session_repo = SQLAlchemyRepository(db, GameSession)
    history_repo = SQLAlchemyRepository(db, UserWordHistory)
    
    return GameService(word_repo, session_repo, history_repo)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency injection for UserService"""
    from app.models import User
    
    user_repo = SQLAlchemyRepository(db, User)
    return UserService(user_repo)

@router.post("/api/game/start")
def start_game_session(
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Start a new game session"""
    try:
        game_type = data.get("game_type")
        
        if not game_type:
            raise GameValidationError("Game type is required")
        
        session = game_service.start_game_session(current_user.id, game_type)
        
        return {
            "session_id": session.id,
            "game_type": game_type,
            "status": "started"
        }
    
    except GameValidationError as e:
        logger.warning(f"Game validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except AppException as e:
        logger.error(f"Application error in start_game_session: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in start_game_session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/api/words/{game_type}")
def get_game_words(
    game_type: str,
    count: int = 5,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Get words for a specific game type"""
    try:
        # Validate count parameter
        if count <= 0 or count > 20:
            raise GameValidationError("Count must be between 1 and 20")
        
        words = game_service.get_game_words(
            user_id=current_user.id,
            game_type=game_type,
            count=count,
            difficulty=difficulty
        )
        
        return words
    
    except GameValidationError as e:
        logger.warning(f"Game validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except AppException as e:
        logger.error(f"Application error in get_game_words: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/api/word/check")
def check_word_answer(
    word_id: int = Body(...),
    answer: str = Body(...),
    game_type: str = Body(...),
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
):
    """Check if user's answer is correct"""
    try:
        # Validate input
        if not answer or not answer.strip():
            raise GameValidationError("Answer cannot be empty")
        
        is_correct = game_service.validate_answer(
            user_id=current_user.id,
            word_id=word_id,
            user_answer=answer,
            game_type=game_type
        )
        
        return {"correct": is_correct}
    
    except WordNotFoundError as e:
        logger.warning(f"Word not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    except GameValidationError as e:
        logger.warning(f"Game validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except AppException as e:
        logger.error(f"Application error in check_word_answer: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/api/game/end")
def end_game_session(
    session_id: int = Body(...),
    score: int = Body(...),
    correct_answers: int = Body(...),
    total_questions: int = Body(...),
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service),
    user_service: UserService = Depends(get_user_service),
):
    """End a game session and update user progress"""
    try:
        # Validate input
        if score < 0:
            raise GameValidationError("Score cannot be negative")
        
        if correct_answers < 0 or total_questions <= 0:
            raise GameValidationError("Invalid answer counts")
        
        if correct_answers > total_questions:
            raise GameValidationError("Correct answers cannot exceed total questions")
        
        # Complete game session
        session = game_service.complete_game_session(
            session_id=session_id,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions
        )
        
        if not session:
            raise GameValidationError("Game session not found")
        
        # Update user experience
        experience_result = user_service.add_experience(
            user_id=current_user.id,
            correct_answers=correct_answers,
            total_questions=total_questions
        )
        
        return {
            "experience_gained": experience_result.experience_gained,
            "total_experience": experience_result.total_experience,
            "level": experience_result.current_level,
            "level_up": experience_result.level_up_occurred,
            "daily_limit_reached": experience_result.daily_limit_reached,
        }
    
    except GameValidationError as e:
        logger.warning(f"Game validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    
    except AppException as e:
        logger.error(f"Application error in end_game_session: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )