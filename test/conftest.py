"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.models import Base, User, Word, GameSession, GameSetting
from app.database import get_db
from app.password_utils import get_password_hash


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using SQLite in memory"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Create engine with SQLite
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    os.unlink(db_path)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create a test client with database dependency override"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(test_db_session):
    """Create a sample user for testing"""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        role="user",
        level=1,
        experience=0,
        total_points=0,
        daily_experience=0,
        created_at=datetime.now(timezone.utc),
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def sample_admin(test_db_session):
    """Create a sample admin user for testing"""
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword"),
        role="admin",
        level=5,
        experience=100,
        total_points=150,
        daily_experience=50,
        created_at=datetime.now(timezone.utc),
    )
    test_db_session.add(admin)
    test_db_session.commit()
    test_db_session.refresh(admin)
    return admin


@pytest.fixture
def sample_words(test_db_session):
    """Create sample words for testing"""
    words = [
        Word(
            text="hello",
            translation="привет",
            description="a greeting",
            difficulty="easy",
            times_shown=0,
            times_correct=0,
            correct_ratio=0.0,
            created_at=datetime.now(timezone.utc),
        ),
        Word(
            text="computer",
            translation="компьютер",
            description="an electronic device",
            difficulty="medium",
            times_shown=5,
            times_correct=3,
            correct_ratio=0.6,
            created_at=datetime.now(timezone.utc),
        ),
        Word(
            text="philosophy",
            translation="философия",
            description="the study of knowledge and existence",
            difficulty="hard",
            times_shown=2,
            times_correct=1,
            correct_ratio=0.5,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    for word in words:
        test_db_session.add(word)

    test_db_session.commit()

    for word in words:
        test_db_session.refresh(word)

    return words


@pytest.fixture
def sample_game_session(test_db_session, sample_user):
    """Create a sample game session for testing"""
    session = GameSession(
        user_id=sample_user.id,
        game_type="scramble",
        score=0,
        started_at=datetime.now(timezone.utc),
        correct_answers=0,
        total_questions=0,
        difficulty_level="easy",
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    return session


@pytest.fixture
def sample_game_settings(test_db_session):
    """Create sample game settings for testing"""
    settings = [
        GameSetting(
            key="points_per_answer",
            value="10",
            description="Points awarded per correct answer",
            category="scoring",
        ),
        GameSetting(
            key="points_for_level_up",
            value="100",
            description="Points needed to level up",
            category="progression",
        ),
        GameSetting(
            key="daily_experience_limit",
            value="200",
            description="Daily experience limit",
            category="limits",
        ),
        GameSetting(
            key="streak_bonus",
            value="5",
            description="Bonus points for perfect score",
            category="scoring",
        ),
    ]

    for setting in settings:
        test_db_session.add(setting)

    test_db_session.commit()

    for setting in settings:
        test_db_session.refresh(setting)

    return settings


@pytest.fixture
def authenticated_user_session(client, sample_user):
    """Create an authenticated user session"""
    # Login the user
    response = client.post("/login", data={"email": sample_user.email, "password": "testpassword"})
    assert response.status_code in [200, 303]  # Success or redirect
    return client


@pytest.fixture
def authenticated_admin_session(client, sample_admin):
    """Create an authenticated admin session"""
    # Login the admin
    response = client.post(
        "/login", data={"email": sample_admin.email, "password": "adminpassword"}
    )
    assert response.status_code in [200, 303]  # Success or redirect
    return client
