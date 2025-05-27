"""
Integration tests for database operations
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

from app import database
from app.models import User, Word, GameSession, UserWordHistory, GameSetting
from tests.conftest import create_test_user, create_test_word


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseOperations:
    """Test database operations"""
    
    def test_create_user(self, test_db_session):
        """Test creating a user through database functions"""
        user = database.create_user(
            test_db_session,
            name="DB Test User",
            email="dbtest@example.com",
            password="testpassword",
            role="user"
        )
        
        assert user.id is not None
        assert user.name == "DB Test User"
        assert user.email == "dbtest@example.com"
        assert user.role == "user"
        assert user.password_hash is not None
        assert user.password_hash != "testpassword"  # Should be hashed
    
    def test_get_user_by_id(self, test_db_session, sample_user):
        """Test retrieving user by ID"""
        user = database.get_user(test_db_session, sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    def test_get_user_by_email(self, test_db_session, sample_user):
        """Test retrieving user by email"""
        user = database.get_user_by_email(test_db_session, sample_user.email)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    def test_get_nonexistent_user(self, test_db_session):
        """Test retrieving nonexistent user"""
        user = database.get_user(test_db_session, 99999)
        assert user is None
        
        user = database.get_user_by_email(test_db_session, "nonexistent@example.com")
        assert user is None
    
    def test_update_user(self, test_db_session, sample_user):
        """Test updating user data"""
        updated_user = database.update_user(
            test_db_session,
            sample_user.id,
            name="Updated Name",
            level=5
        )
        
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        assert updated_user.level == 5
        assert updated_user.email == sample_user.email  # Unchanged
    
    def test_update_user_password(self, test_db_session, sample_user):
        """Test updating user password"""
        original_hash = sample_user.password_hash
        
        updated_user = database.update_user(
            test_db_session,
            sample_user.id,
            password="newpassword"
        )
        
        assert updated_user is not None
        assert updated_user.password_hash != original_hash
        assert updated_user.password_hash != "newpassword"  # Should be hashed
    
    def test_update_user_last_login(self, test_db_session, sample_user):
        """Test updating user last login time"""
        original_last_login = sample_user.last_login
        
        database.update_user_last_login(test_db_session, sample_user.id)
        
        test_db_session.refresh(sample_user)
        assert sample_user.last_login != original_last_login
        assert sample_user.last_login is not None
    
    def test_get_user_stats(self, test_db_session, sample_user):
        """Test getting user statistics"""
        # Create some game sessions for the user
        session1 = GameSession(
            user_id=sample_user.id,
            game_type="scramble",
            correct_answers=8,
            total_questions=10,
            score=80
        )
        session2 = GameSession(
            user_id=sample_user.id,
            game_type="matching",
            correct_answers=5,
            total_questions=7,
            score=50
        )
        
        test_db_session.add(session1)
        test_db_session.add(session2)
        test_db_session.commit()
        
        stats = database.get_user_stats(test_db_session, sample_user.id)
        
        assert stats is not None
        assert stats["level"] == sample_user.level
        assert stats["experience"] == sample_user.experience
        assert stats["total_games"] == 2
        assert stats["correct_answers"] == 13  # 8 + 5
    
    def test_get_users_statistics(self, test_db_session, sample_user, sample_admin):
        """Test getting users statistics"""
        stats = database.get_users_statistics(test_db_session)
        
        assert stats is not None
        assert "total_users" in stats
        assert "new_users_30_days" in stats
        assert "active_users_7_days" in stats
        assert "level_distribution" in stats
        
        assert stats["total_users"] >= 2  # At least sample_user and sample_admin
        assert isinstance(stats["level_distribution"], dict)
    
    def test_create_word(self, test_db_session):
        """Test creating a word through database functions"""
        word = database.create_word(
            test_db_session,
            text="database",
            translation="база данных",
            description="a collection of data",
            difficulty="medium"
        )
        
        assert word.id is not None
        assert word.text == "database"
        assert word.translation == "база данных"
        assert word.description == "a collection of data"
        assert word.difficulty == "medium"
        assert word.times_shown == 0
        assert word.times_correct == 0
    
    def test_get_random_words(self, test_db_session, sample_user, sample_words):
        """Test getting random words"""
        words = database.get_random_words(
            test_db_session,
            sample_user.id,
            count=2,
            difficulty="easy"
        )
        
        assert len(words) <= 2
        for word in words:
            assert word.difficulty == "easy"
    
    def test_get_random_words_with_exclusions(self, test_db_session, sample_user, sample_words):
        """Test getting random words with exclusions"""
        # Exclude first word
        excluded_ids = [sample_words[0].id]
        
        words = database.get_random_words(
            test_db_session,
            sample_user.id,
            count=5,
            excluded_ids=excluded_ids
        )
        
        # Should not contain excluded word
        returned_ids = [word.id for word in words]
        assert sample_words[0].id not in returned_ids
    
    def test_update_word_stats(self, test_db_session, sample_words):
        """Test updating word statistics"""
        word = sample_words[0]
        original_shown = word.times_shown
        original_correct = word.times_correct
        
        # Update with correct answer
        database.update_word_stats(test_db_session, word.id, True)
        
        test_db_session.refresh(word)
        assert word.times_correct == original_correct + 1
    
    def test_add_user_experience(self, test_db_session, sample_user, sample_game_settings):
        """Test adding experience to user"""
        original_exp = sample_user.experience
        original_level = sample_user.level
        
        user, level_up, daily_limit_reached = database.add_user_experience(
            test_db_session,
            sample_user.id,
            50  # Add 50 experience
        )
        
        assert user is not None
        assert user.experience >= original_exp  # Could level up and reset experience
        assert isinstance(level_up, bool)
        assert isinstance(daily_limit_reached, bool)
    
    def test_add_user_experience_level_up(self, test_db_session, sample_user, sample_game_settings):
        """Test adding enough experience to level up"""
        # Set user to near level up (99 experience, needs 100 for level up)
        sample_user.experience = 99
        test_db_session.commit()
        
        user, level_up, daily_limit_reached = database.add_user_experience(
            test_db_session,
            sample_user.id,
            10  # Add 10 experience (should trigger level up)
        )
        
        assert level_up is True
        assert user.level == sample_user.level + 1
    
    def test_add_user_experience_daily_limit(self, test_db_session, sample_user, sample_game_settings):
        """Test daily experience limit"""
        # Set user to near daily limit
        sample_user.daily_experience = 190  # Limit is 200
        sample_user.daily_experience_updated_at = datetime.now(timezone.utc)
        test_db_session.commit()
        
        user, level_up, daily_limit_reached = database.add_user_experience(
            test_db_session,
            sample_user.id,
            20  # Would exceed daily limit
        )
        
        assert daily_limit_reached is True
        assert user.daily_experience <= 200  # Should not exceed limit
    
    def test_create_game_session(self, test_db_session, sample_user):
        """Test creating a game session"""
        session = database.create_game_session(
            test_db_session,
            sample_user.id,
            "scramble"
        )
        
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.game_type == "scramble"
        assert session.started_at is not None
        assert session.completed_at is None
    
    def test_complete_game_session(self, test_db_session, sample_game_session):
        """Test completing a game session"""
        session = database.complete_game_session(
            test_db_session,
            sample_game_session.id,
            score=150,
            correct_answers=8,
            total_questions=10
        )
        
        assert session is not None
        assert session.score == 150
        assert session.correct_answers == 8
        assert session.total_questions == 10
        assert session.completed_at is not None
    
    def test_get_user_game_history(self, test_db_session, sample_user):
        """Test getting user game history"""
        # Create multiple game sessions
        for i in range(3):
            session = GameSession(
                user_id=sample_user.id,
                game_type="scramble",
                score=i * 50,
                completed_at=datetime.now(timezone.utc)
            )
            test_db_session.add(session)
        
        test_db_session.commit()
        
        history = database.get_user_game_history(test_db_session, sample_user.id, limit=2)
        
        assert len(history) <= 2
        # Should be ordered by most recent first
        if len(history) > 1:
            assert history[0].started_at >= history[1].started_at
    
    def test_game_settings_operations(self, test_db_session):
        """Test game settings operations"""
        # Set a setting
        setting = database.set_game_setting(test_db_session, "test_key", "test_value")
        
        assert setting.key == "test_key"
        assert setting.value == "test_value"
        
        # Get the setting
        value = database.get_game_setting(test_db_session, "test_key", "default")
        assert value == "test_value"
        
        # Get nonexistent setting
        value = database.get_game_setting(test_db_session, "nonexistent", "default")
        assert value == "default"
        
        # Get setting as int
        database.set_game_setting(test_db_session, "int_key", "42")
        int_value = database.get_game_setting_int(test_db_session, "int_key", 0)
        assert int_value == 42
        
        # Get invalid int setting
        database.set_game_setting(test_db_session, "invalid_int", "not_a_number")
        int_value = database.get_game_setting_int(test_db_session, "invalid_int", 10)
        assert int_value == 10  # Should return default
    
    def test_get_all_game_settings(self, test_db_session, sample_game_settings):
        """Test getting all game settings"""
        settings = database.get_all_game_settings(test_db_session)
        
        assert isinstance(settings, dict)
        assert len(settings) >= len(sample_game_settings)
        
        # Check that sample settings are included
        for setting in sample_game_settings:
            assert setting.key in settings
            assert settings[setting.key] == setting.value
    
    def test_get_words_statistics(self, test_db_session, sample_words, sample_user):
        """Test getting words statistics"""
        # Create some word history
        for word in sample_words[:2]:
            history = UserWordHistory(
                user_id=sample_user.id,
                word_id=word.id,
                correct=True,
                game_type="scramble",
                used_at=datetime.now(timezone.utc)
            )
            test_db_session.add(history)
        
        test_db_session.commit()
        
        stats = database.get_words_statistics(test_db_session)
        
        assert stats is not None
        assert "total_words" in stats
        assert "difficulty_distribution" in stats
        assert "most_used_words" in stats
        assert "problematic_words" in stats
        assert "usage_stats" in stats
        
        assert stats["total_words"] >= len(sample_words)
        assert isinstance(stats["difficulty_distribution"], dict)
        assert isinstance(stats["most_used_words"], list)
        assert isinstance(stats["usage_stats"], list)
    
    def test_database_transactions(self, test_db_session):
        """Test database transaction handling"""
        # Test successful transaction
        user = User(
            name="Transaction Test",
            email="transaction@example.com",
            password_hash="hash"
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        
        # Verify user was created
        created_user = test_db_session.query(User).filter(User.email == "transaction@example.com").first()
        assert created_user is not None
        
        # Test rollback
        try:
            duplicate_user = User(
                name="Duplicate",
                email="transaction@example.com",  # Same email - should fail
                password_hash="hash"
            )
            test_db_session.add(duplicate_user)
            test_db_session.commit()
        except Exception:
            test_db_session.rollback()
        
        # Verify no duplicate was created
        users = test_db_session.query(User).filter(User.email == "transaction@example.com").all()
        assert len(users) == 1
    
    def test_database_constraints(self, test_db_session, sample_user):
        """Test database constraints are enforced"""
        # Test unique email constraint
        with pytest.raises(Exception):  # Should raise IntegrityError or similar
            duplicate_user = User(
                name="Duplicate",
                email=sample_user.email,  # Duplicate email
                password_hash="hash"
            )
            test_db_session.add(duplicate_user)
            test_db_session.commit()
    
    def test_cascading_deletes(self, test_db_session, sample_user):
        """Test that cascading deletes work properly"""
        # Create a game session for the user
        session = GameSession(
            user_id=sample_user.id,
            game_type="scramble",
            score=100
        )
        test_db_session.add(session)
        test_db_session.commit()
        
        session_id = session.id
        
        # Delete the user
        test_db_session.delete(sample_user)
        test_db_session.commit()
        
        # Verify the game session was also deleted (cascade)
        deleted_session = test_db_session.query(GameSession).filter(GameSession.id == session_id).first()
        assert deleted_session is None