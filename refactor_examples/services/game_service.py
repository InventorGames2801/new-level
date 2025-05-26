"""
Game service implementing business logic with proper separation of concerns
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta

from app.models import User, Word, GameSession, UserWordHistory
from .game_strategies import GameStrategyFactory, GameStrategy
from ..repositories.base_repository import BaseRepository
from ..exceptions import GameValidationError, WordNotFoundError

class GameService:
    """Service for handling game business logic"""
    
    def __init__(
        self,
        word_repository: BaseRepository[Word],
        game_session_repository: BaseRepository[GameSession],
        user_word_history_repository: BaseRepository[UserWordHistory],
        strategy_factory: GameStrategyFactory = GameStrategyFactory
    ):
        self.word_repository = word_repository
        self.game_session_repository = game_session_repository
        self.user_word_history_repository = user_word_history_repository
        self.strategy_factory = strategy_factory
    
    def start_game_session(self, user_id: int, game_type: str) -> GameSession:
        """Start a new game session"""
        # Validate game type
        if game_type not in self.strategy_factory.get_available_game_types():
            raise GameValidationError(f"Invalid game type: {game_type}")
        
        session_data = {
            "user_id": user_id,
            "game_type": game_type,
            "started_at": datetime.now(timezone.utc),
        }
        
        return self.game_session_repository.create(session_data)
    
    def get_game_words(
        self,
        user_id: int,
        game_type: str,
        count: int = 5,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get words for a game session"""
        # Get strategy for the game type
        strategy = self.strategy_factory.create_strategy(game_type)
        
        # Get excluded words (recently used)
        excluded_ids = self._get_recently_used_words(user_id)
        
        # Get random words
        words = self._get_random_words(user_id, count, difficulty, excluded_ids)
        
        # Prepare questions using strategy
        return [strategy.prepare_question(word) for word in words]
    
    def validate_answer(
        self,
        user_id: int,
        word_id: int,
        user_answer: str,
        game_type: str
    ) -> bool:
        """Validate user's answer"""
        # Get word
        word = self.word_repository.get_by_id(word_id)
        if not word:
            raise WordNotFoundError(f"Word with id {word_id} not found")
        
        # Get strategy and validate
        strategy = self.strategy_factory.create_strategy(game_type)
        is_correct = strategy.validate_answer(word, user_answer)
        
        # Record the attempt
        self._record_word_attempt(user_id, word_id, game_type, is_correct)
        
        # Update word statistics
        self._update_word_statistics(word, is_correct)
        
        return is_correct
    
    def complete_game_session(
        self,
        session_id: int,
        score: int,
        correct_answers: int,
        total_questions: int
    ) -> Optional[GameSession]:
        """Complete a game session"""
        session_data = {
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "completed_at": datetime.now(timezone.utc),
        }
        
        return self.game_session_repository.update(session_id, session_data)
    
    def _get_recently_used_words(self, user_id: int, hours: int = 48) -> List[int]:
        """Get IDs of words used by user in the last N hours"""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        # This would need to be implemented in the repository
        # For now, returning empty list
        return []
    
    def _get_random_words(
        self,
        user_id: int,
        count: int,
        difficulty: Optional[str],
        excluded_ids: List[int]
    ) -> List[Word]:
        """Get random words excluding recently used ones"""
        # This would need to be implemented in the word repository
        # For now, returning empty list
        return []
    
    def _record_word_attempt(
        self,
        user_id: int,
        word_id: int,
        game_type: str,
        is_correct: bool
    ) -> None:
        """Record user's attempt at a word"""
        attempt_data = {
            "user_id": user_id,
            "word_id": word_id,
            "game_type": game_type,
            "correct": is_correct,
            "used_at": datetime.now(timezone.utc),
        }
        
        self.user_word_history_repository.create(attempt_data)
    
    def _update_word_statistics(self, word: Word, is_correct: bool) -> None:
        """Update word statistics"""
        updates = {"times_shown": word.times_shown + 1}
        
        if is_correct:
            updates["times_correct"] = word.times_correct + 1
        
        # Calculate new correct ratio
        new_correct_ratio = updates.get("times_correct", word.times_correct) / updates["times_shown"]
        updates["correct_ratio"] = new_correct_ratio
        updates["last_used_at"] = datetime.now(timezone.utc)
        
        self.word_repository.update(word.id, updates)