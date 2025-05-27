from app.models import User, Word
from app.password_utils import get_password_hash
from datetime import datetime, timezone


class TestData:
    """Constants for test data"""

    VALID_USER_DATA = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "newpassword",
    }

    VALID_WORD_DATA = {
        "text": "test",
        "translation": "тест",
        "description": "a trial or examination",
        "difficulty": "easy",
    }

    VALID_GAME_TYPES = ["scramble", "matching", "typing"]
    VALID_DIFFICULTIES = ["easy", "medium", "hard"]

    INVALID_EMAILS = ["invalid-email", "", "test@", "@example.com", "test.example.com"]

    INVALID_PASSWORDS = [
        "",
        "123",
        " ",
    ]


def create_test_user(db_session, **kwargs):
    """Helper function to create a test user with custom parameters"""
    default_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": get_password_hash("testpassword"),
        "role": "user",
        "level": 1,
        "experience": 0,
        "total_points": 0,
        "daily_experience": 0,
        "created_at": datetime.now(timezone.utc),
    }
    default_data.update(kwargs)
    user = User(**default_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_word(db_session, **kwargs):
    """Helper function to create a test word with custom parameters"""
    default_data = {
        "text": "test",
        "translation": "тест",
        "description": "a test word",
        "difficulty": "easy",
        "times_shown": 0,
        "times_correct": 0,
        "correct_ratio": 0.0,
        "created_at": datetime.now(timezone.utc),
    }
    default_data.update(kwargs)
    word = Word(**default_data)
    db_session.add(word)
    db_session.commit()
    db_session.refresh(word)
    return word
