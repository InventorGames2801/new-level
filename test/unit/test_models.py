"""
Unit tests for SQLAlchemy models
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models import User, Word, GameSession, UserWordHistory, GameSetting
from app.password_utils import get_password_hash


@pytest.mark.unit
class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, test_db_session):
        """Test creating a new user"""
        user = User(
            name="Test User",
            email="test@example.com",
            password_hash=get_password_hash("testpassword"),
            role="user"
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.level == 1  # Default value
        assert user.experience == 0  # Default value
        assert user.total_points == 0  # Default value
        assert user.created_at is not None
    
    def test_user_email_uniqueness(self, test_db_session):
        """Test that user emails must be unique"""
        user1 = User(
            name="User 1",
            email="test@example.com",
            password_hash=get_password_hash("password1"),
        )
        
        user2 = User(
            name="User 2",
            email="test@example.com",  # Same email
            password_hash=get_password_hash("password2"),
        )
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        test_db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_user_default_values(self, test_db_session):
        """Test user model default values"""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("testpassword")
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.role == "user"
        assert user.level == 1
        assert user.experience == 0
        assert user.total_points == 0
        assert user.daily_experience == 0
    
    def test_user_relationships(self, test_db_session, sample_user):
        """Test user model relationships"""
        # Create a game session for the user
        session = GameSession(
            user_id=sample_user.id,
            game_type="scramble",
            score=100
        )
        test_db_session.add(session)
        test_db_session.commit()
        
        # Test the relationship
        test_db_session.refresh(sample_user)
        assert len(sample_user.games_history) == 1
        assert sample_user.games_history[0].game_type == "scramble"


@pytest.mark.unit
class TestWordModel:
    """Test Word model"""
    
    def test_create_word(self, test_db_session):
        """Test creating a new word"""
        word = Word(
            text="hello",
            translation="привет",
            description="a greeting",
            difficulty="easy"
        )
        
        test_db_session.add(word)
        test_db_session.commit()
        test_db_session.refresh(word)
        
        assert word.id is not None
        assert word.text == "hello"
        assert word.translation == "привет"
        assert word.description == "a greeting"
        assert word.difficulty == "easy"
        assert word.times_shown == 0  # Default value
        assert word.times_correct == 0  # Default value
        assert word.correct_ratio == 0.0  # Default value
        assert word.created_at is not None
    
    def test_word_required_fields(self, test_db_session):
        """Test that required fields are enforced"""
        with pytest.raises(TypeError):
            # Missing required fields should raise TypeError
            word = Word()
            test_db_session.add(word)
            test_db_session.commit()
    
    def test_word_statistics_update(self, test_db_session):
        """Test updating word statistics"""
        word = Word(
            text="test",
            translation="тест",
            description="a test",
            difficulty="easy",
            times_shown=10,
            times_correct=7
        )
        
        test_db_session.add(word)
        test_db_session.commit()
        
        # Update statistics
        word.times_shown += 1
        word.times_correct += 1
        word.correct_ratio = word.times_correct / word.times_shown
        
        test_db_session.commit()
        test_db_session.refresh(word)
        
        assert word.times_shown == 11
        assert word.times_correct == 8
        assert abs(word.correct_ratio - (8/11)) < 0.001  # Float comparison


@pytest.mark.unit
class TestGameSessionModel:
    """Test GameSession model"""
    
    def test_create_game_session(self, test_db_session, sample_user):
        """Test creating a new game session"""
        session = GameSession(
            user_id=sample_user.id,
            game_type="scramble",
            score=150,
            correct_answers=8,
            total_questions=10
        )
        
        test_db_session.add(session)
        test_db_session.commit()
        test_db_session.refresh(session)
        
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.game_type == "scramble"
        assert session.score == 150
        assert session.correct_answers == 8
        assert session.total_questions == 10
        assert session.started_at is not None
        assert session.difficulty_level == "easy"  # Default value
    
    def test_game_session_user_relationship(self, test_db_session, sample_user):
        """Test game session relationship with user"""
        session = GameSession(
            user_id=sample_user.id,
            game_type="matching",
            score=200
        )
        
        test_db_session.add(session)
        test_db_session.commit()
        test_db_session.refresh(session)
        
        assert session.user.id == sample_user.id
        assert session.user.email == sample_user.email


@pytest.mark.unit
class TestUserWordHistoryModel:
    """Test UserWordHistory model"""
    
    def test_create_word_history(self, test_db_session, sample_user, sample_words):
        """Test creating a word history entry"""
        word = sample_words[0]
        
        history = UserWordHistory(
            user_id=sample_user.id,
            word_id=word.id,
            correct=True,
            game_type="scramble"
        )
        
        test_db_session.add(history)
        test_db_session.commit()
        test_db_session.refresh(history)
        
        assert history.id is not None
        assert history.user_id == sample_user.id
        assert history.word_id == word.id
        assert history.correct is True
        assert history.game_type == "scramble"
        assert history.used_at is not None
    
    def test_word_history_relationships(self, test_db_session, sample_user, sample_words):
        """Test word history relationships"""
        word = sample_words[0]
        
        history = UserWordHistory(
            user_id=sample_user.id,
            word_id=word.id,
            correct=False,
            game_type="typing"
        )
        
        test_db_session.add(history)
        test_db_session.commit()
        test_db_session.refresh(history)
        
        assert history.user.id == sample_user.id
        assert history.word.id == word.id
        assert history.word.text == word.text


@pytest.mark.unit
class TestGameSettingModel:
    """Test GameSetting model"""
    
    def test_create_game_setting(self, test_db_session):
        """Test creating a game setting"""
        setting = GameSetting(
            key="test_setting",
            value="test_value",
            description="A test setting",
            category="test"
        )
        
        test_db_session.add(setting)
        test_db_session.commit()
        test_db_session.refresh(setting)
        
        assert setting.id is not None
        assert setting.key == "test_setting"
        assert setting.value == "test_value"
        assert setting.description == "A test setting"
        assert setting.category == "test"
    
    def test_game_setting_key_uniqueness(self, test_db_session):
        """Test that game setting keys must be unique"""
        setting1 = GameSetting(
            key="duplicate_key",
            value="value1"
        )
        
        setting2 = GameSetting(
            key="duplicate_key",  # Same key
            value="value2"
        )
        
        test_db_session.add(setting1)
        test_db_session.commit()
        
        test_db_session.add(setting2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_game_setting_default_values(self, test_db_session):
        """Test game setting default values"""
        setting = GameSetting(
            key="test_key",
            value="test_value"
        )
        
        test_db_session.add(setting)
        test_db_session.commit()
        test_db_session.refresh(setting)
        
        assert setting.category == "system"  # Default value