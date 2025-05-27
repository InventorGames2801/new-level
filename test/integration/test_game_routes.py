"""
Integration tests for game routes
"""

import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.game
class TestGameRoutes:
    """Test game-related routes"""

    def test_game_page_authenticated(
        self, authenticated_user_session, sample_words, sample_game_settings
    ):
        """Test GET /game with authenticated user"""
        response = authenticated_user_session.get("/game")

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

    def test_game_page_unauthenticated(self, client):
        """Test GET /game without authentication"""
        response = client.get("/game")

        # Should return 401 or redirect to login
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_303_SEE_OTHER]

    def test_start_game_session_valid(self, authenticated_user_session):
        """Test POST /api/game/start with valid data"""
        response = authenticated_user_session.post(
            "/api/game/start", json={"game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert data["game_type"] == "scramble"

    def test_start_game_session_invalid_type(self, authenticated_user_session):
        """Test POST /api/game/start with invalid game type"""
        response = authenticated_user_session.post(
            "/api/game/start", json={"game_type": "invalid_type"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_game_session_missing_type(self, authenticated_user_session):
        """Test POST /api/game/start without game type"""
        response = authenticated_user_session.post("/api/game/start", json={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_game_session_unauthenticated(self, client):
        """Test POST /api/game/start without authentication"""
        response = client.post("/api/game/start", json={"game_type": "scramble"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("game_type", ["scramble", "matching", "typing"])
    def test_get_game_words_valid_types(self, authenticated_user_session, sample_words, game_type):
        """Test GET /api/words/{game_type} with valid game types"""
        response = authenticated_user_session.get(f"/api/words/{game_type}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # Verify response structure based on game type
        if data:  # If words are returned
            word = data[0]
            assert "id" in word
            assert "difficulty" in word

            if game_type == "scramble":
                assert "scrambled" in word
                assert "description" in word
            elif game_type == "matching":
                assert "text" in word
                assert "description" in word
            elif game_type == "typing":
                assert "description" in word

    def test_get_game_words_invalid_type(self, authenticated_user_session):
        """Test GET /api/words/{game_type} with invalid game type"""
        response = authenticated_user_session.get("/api/words/invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_game_words_with_count(self, authenticated_user_session, sample_words):
        """Test GET /api/words/{game_type} with count parameter"""
        response = authenticated_user_session.get("/api/words/scramble?count=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2  # Should return at most 2 words

    def test_get_game_words_with_difficulty(self, authenticated_user_session, sample_words):
        """Test GET /api/words/{game_type} with difficulty parameter"""
        response = authenticated_user_session.get("/api/words/scramble?difficulty=easy")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # All returned words should have easy difficulty
        for word in data:
            assert word["difficulty"] == "easy"

    def test_get_game_words_invalid_count(self, authenticated_user_session):
        """Test GET /api/words/{game_type} with invalid count"""
        response = authenticated_user_session.get("/api/words/scramble?count=25")  # Above limit

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_game_words_unauthenticated(self, client):
        """Test GET /api/words/{game_type} without authentication"""
        response = client.get("/api/words/scramble")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_check_word_answer_correct(self, authenticated_user_session, sample_words):
        """Test POST /api/word/check with correct answer"""
        word = sample_words[0]  # "hello"

        response = authenticated_user_session.post(
            "/api/word/check", json={"word_id": word.id, "answer": "hello", "game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] is True

    def test_check_word_answer_incorrect(self, authenticated_user_session, sample_words):
        """Test POST /api/word/check with incorrect answer"""
        word = sample_words[0]  # "hello"

        response = authenticated_user_session.post(
            "/api/word/check", json={"word_id": word.id, "answer": "wrong", "game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] is False

    def test_check_word_answer_case_insensitive(self, authenticated_user_session, sample_words):
        """Test POST /api/word/check is case insensitive"""
        word = sample_words[0]  # "hello"

        response = authenticated_user_session.post(
            "/api/word/check", json={"word_id": word.id, "answer": "HELLO", "game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] is True

    def test_check_word_answer_matching_game(self, authenticated_user_session, sample_words):
        """Test POST /api/word/check for matching game type"""
        word = sample_words[0]  # "hello" -> "привет"

        response = authenticated_user_session.post(
            "/api/word/check",
            json={"word_id": word.id, "answer": "привет", "game_type": "matching"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] is True

    def test_check_word_answer_typing_game(self, authenticated_user_session, sample_words):
        """Test POST /api/word/check for typing game type"""
        word = sample_words[0]  # "hello"

        response = authenticated_user_session.post(
            "/api/word/check", json={"word_id": word.id, "answer": "hello", "game_type": "typing"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["correct"] is True

    def test_check_word_answer_nonexistent_word(self, authenticated_user_session):
        """Test POST /api/word/check with nonexistent word ID"""
        response = authenticated_user_session.post(
            "/api/word/check", json={"word_id": 99999, "answer": "test", "game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_check_word_answer_missing_data(self, authenticated_user_session):
        """Test POST /api/word/check with missing data"""
        response = authenticated_user_session.post(
            "/api/word/check",
            json={
                "word_id": 1
                # Missing answer and game_type
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_check_word_answer_unauthenticated(self, client, sample_words):
        """Test POST /api/word/check without authentication"""
        word = sample_words[0]

        response = client.post(
            "/api/word/check", json={"word_id": word.id, "answer": "hello", "game_type": "scramble"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_end_game_session_valid(self, authenticated_user_session, sample_game_session):
        """Test POST /api/game/end with valid data"""
        response = authenticated_user_session.post(
            "/api/game/end",
            json={
                "session_id": sample_game_session.id,
                "score": 100,
                "correct_answers": 5,
                "total_questions": 10,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "experience_gained" in data
        assert "total_experience" in data
        assert "level" in data
        assert "level_up" in data

    def test_end_game_session_nonexistent(self, authenticated_user_session):
        """Test POST /api/game/end with nonexistent session"""
        response = authenticated_user_session.post(
            "/api/game/end",
            json={"session_id": 99999, "score": 100, "correct_answers": 5, "total_questions": 10},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_end_game_session_invalid_data(self, authenticated_user_session, sample_game_session):
        """Test POST /api/game/end with invalid data"""
        response = authenticated_user_session.post(
            "/api/game/end",
            json={
                "session_id": sample_game_session.id,
                "score": -10,  # Negative score
                "correct_answers": 5,
                "total_questions": 10,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_end_game_session_impossible_answers(
        self, authenticated_user_session, sample_game_session
    ):
        """Test POST /api/game/end with impossible answer counts"""
        response = authenticated_user_session.post(
            "/api/game/end",
            json={
                "session_id": sample_game_session.id,
                "score": 100,
                "correct_answers": 15,  # More correct than total
                "total_questions": 10,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_end_game_session_unauthenticated(self, client, sample_game_session):
        """Test POST /api/game/end without authentication"""
        response = client.post(
            "/api/game/end",
            json={
                "session_id": sample_game_session.id,
                "score": 100,
                "correct_answers": 5,
                "total_questions": 10,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_translation_options(self, authenticated_user_session, sample_words):
        """Test GET /api/translation-options"""
        response = authenticated_user_session.get("/api/translation-options")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        # Check structure of options
        for option in data:
            assert "text" in option

    def test_get_translation_options_with_count(self, authenticated_user_session, sample_words):
        """Test GET /api/translation-options with count parameter"""
        response = authenticated_user_session.get("/api/translation-options?count=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2

    def test_check_matching_answers(self, authenticated_user_session, sample_words):
        """Test POST /api/matching/check"""
        word = sample_words[0]  # "hello" -> "привет"

        response = authenticated_user_session.post(
            "/api/matching/check", json=[{"wordId": word.id, "answer": "привет"}]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "all_correct" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_debug_word_count(self, authenticated_user_session, sample_words):
        """Test GET /api/debug/word-count"""
        response = authenticated_user_session.get("/api/debug/word-count")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert data["count"] >= len(sample_words)

    def test_game_flow_integration(
        self, authenticated_user_session, sample_words, sample_game_settings
    ):
        """Test complete game flow integration"""
        # 1. Start game session
        start_response = authenticated_user_session.post(
            "/api/game/start", json={"game_type": "scramble"}
        )
        assert start_response.status_code == status.HTTP_200_OK
        session_data = start_response.json()
        session_id = session_data["session_id"]

        # 2. Get words
        words_response = authenticated_user_session.get("/api/words/scramble?count=3")
        assert words_response.status_code == status.HTTP_200_OK
        words = words_response.json()

        # 3. Check answers for all words
        correct_answers = 0
        total_questions = len(words)

        for word_data in words:
            # For this test, we'll get the correct answer from the original word
            # In a real game, the player would need to unscramble
            check_response = authenticated_user_session.post(
                "/api/word/check",
                json={
                    "word_id": word_data["id"],
                    "answer": "hello",  # Assuming first word is "hello"
                    "game_type": "scramble",
                },
            )
            assert check_response.status_code == status.HTTP_200_OK
            if check_response.json()["correct"]:
                correct_answers += 1

        # 4. End game session
        end_response = authenticated_user_session.post(
            "/api/game/end",
            json={
                "session_id": session_id,
                "score": correct_answers * 10,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
            },
        )
        assert end_response.status_code == status.HTTP_200_OK

        # Verify final response structure
        end_data = end_response.json()
        assert "experience_gained" in end_data
        assert "total_experience" in end_data
        assert "level" in end_data
