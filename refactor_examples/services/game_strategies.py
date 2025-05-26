"""
Game strategies implementing Open/Closed Principle
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models import Word
from app.game_utils import create_scrambled_word

class GameStrategy(ABC):
    """Abstract base class for game strategies"""
    
    @abstractmethod
    def prepare_question(self, word: Word) -> Dict[str, Any]:
        """Prepare question data for the frontend"""
        pass
    
    @abstractmethod
    def validate_answer(self, word: Word, user_answer: str) -> bool:
        """Validate user's answer"""
        pass
    
    @abstractmethod
    def get_game_type(self) -> str:
        """Return the game type identifier"""
        pass

class ScrambleGameStrategy(GameStrategy):
    """Strategy for word scrambling game"""
    
    def prepare_question(self, word: Word) -> Dict[str, Any]:
        return {
            "id": word.id,
            "scrambled": create_scrambled_word(word.text),
            "description": word.description,
            "difficulty": word.difficulty,
        }
    
    def validate_answer(self, word: Word, user_answer: str) -> bool:
        return word.text.lower().strip() == user_answer.lower().strip()
    
    def get_game_type(self) -> str:
        return "scramble"

class MatchingGameStrategy(GameStrategy):
    """Strategy for word-translation matching game"""
    
    def prepare_question(self, word: Word) -> Dict[str, Any]:
        return {
            "id": word.id,
            "text": word.text,
            "description": word.description,
            "difficulty": word.difficulty,
        }
    
    def validate_answer(self, word: Word, user_answer: str) -> bool:
        return word.translation.lower().strip() == user_answer.lower().strip()
    
    def get_game_type(self) -> str:
        return "matching"

class TypingGameStrategy(GameStrategy):
    """Strategy for typing game"""
    
    def prepare_question(self, word: Word) -> Dict[str, Any]:
        return {
            "id": word.id,
            "description": word.description,
            "difficulty": word.difficulty,
        }
    
    def validate_answer(self, word: Word, user_answer: str) -> bool:
        return word.text.lower().strip() == user_answer.lower().strip()
    
    def get_game_type(self) -> str:
        return "typing"

class GameStrategyFactory:
    """Factory for creating game strategies"""
    
    _strategies = {
        "scramble": ScrambleGameStrategy,
        "matching": MatchingGameStrategy,
        "typing": TypingGameStrategy,
    }
    
    @classmethod
    def create_strategy(cls, game_type: str) -> GameStrategy:
        """Create and return a game strategy instance"""
        if game_type not in cls._strategies:
            raise ValueError(f"Unknown game type: {game_type}")
        
        return cls._strategies[game_type]()
    
    @classmethod
    def get_available_game_types(cls) -> list[str]:
        """Return list of available game types"""
        return list(cls._strategies.keys())
    
    @classmethod
    def register_strategy(cls, game_type: str, strategy_class: type):
        """Register a new game strategy (for extensibility)"""
        if not issubclass(strategy_class, GameStrategy):
            raise ValueError("Strategy must inherit from GameStrategy")
        
        cls._strategies[game_type] = strategy_class