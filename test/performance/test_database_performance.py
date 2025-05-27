"""
Performance tests for database operations
"""
import pytest
import time
from sqlalchemy import text

from app.models import User, Word, GameSession
from tests.conftest import create_test_user, create_test_word


@pytest.mark.slow
@pytest.mark.database
class TestDatabasePerformance:
    """Test database operation performance"""
    
    def test_bulk_user_creation_performance(self, test_db_session):
        """Test performance of creating many users"""
        start_time = time.time()
        
        users = []
        for i in range(100):
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash="hashed_password",
                role="user"
            )
            users.append(user)
        
        test_db_session.add_all(users)
        test_db_session.commit()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust as needed)
        assert duration < 5.0, f"Bulk user creation took {duration:.2f}s, expected < 5s"
        
        # Verify all users were created
        user_count = test_db_session.query(User).count()
        assert user_count >= 100
    
    def test_bulk_word_creation_performance(self, test_db_session):
        """Test performance of creating many words"""
        start_time = time.time()
        
        words = []
        for i in range(200):
            word = Word(
                text=f"word{i}",
                translation=f"слово{i}",
                description=f"Description for word {i}",
                difficulty="easy" if i % 3 == 0 else "medium" if i % 3 == 1 else "hard",
                times_shown=0,
                times_correct=0,
                correct_ratio=0.0
            )
            words.append(word)
        
        test_db_session.add_all(words)
        test_db_session.commit()
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 10.0, f"Bulk word creation took {duration:.2f}s, expected < 10s"
        
        # Verify all words were created
        word_count = test_db_session.query(Word).count()
        assert word_count >= 200
    
    def test_word_search_performance(self, test_db_session):
        """Test performance of word search operations"""
        # Create test words
        words = []
        for i in range(500):
            word = Word(
                text=f"searchword{i}",
                translation=f"поиск{i}",
                description=f"Search description {i}",
                difficulty="easy" if i % 3 == 0 else "medium" if i % 3 == 1 else "hard",
                times_shown=i % 10,
                times_correct=i % 7,
                correct_ratio=(i % 7) / max(1, i % 10)
            )
            words.append(word)
        
        test_db_session.add_all(words)
        test_db_session.commit()
        
        # Test various search operations
        search_operations = [
            lambda: test_db_session.query(Word).filter(Word.difficulty == "easy").all(),
            lambda: test_db_session.query(Word).filter(Word.times_shown > 5).all(),
            lambda: test_db_session.query(Word).filter(Word.correct_ratio > 0.5).all(),
            lambda: test_db_session.query(Word).filter(Word.text.like("searchword1%")).all(),
        ]
        
        for operation in search_operations:
            start_time = time.time()
            results = operation()
            end_time = time.time()
            duration = end_time - start_time
            
            assert duration < 1.0, f"Search operation took {duration:.2f}s, expected < 1s"
            assert len(results) > 0, "Search should return results"
    
    def test_user_stats_calculation_performance(self, test_db_session):
        """Test performance of user statistics calculation"""
        # Create test user
        user = create_test_user(test_db_session, email="statsuser@example.com")
        
        # Create many game sessions
        sessions = []
        for i in range(100):
            session = GameSession(
                user_id=user.id,
                game_type="scramble" if i % 2 == 0 else "matching",
                score=i * 10,
                correct_answers=i % 10,
                total_questions=10,
                difficulty_level="easy" if i % 3 == 0 else "medium" if i % 3 == 1 else "hard"
            )
            sessions.append(session)
        
        test_db_session.add_all(sessions)
        test_db_session.commit()
        
        # Test stats calculation performance
        from app.database import get_user_stats
        
        start_time = time.time()
        stats = get_user_stats(test_db_session, user.id)
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 2.0, f"User stats calculation took {duration:.2f}s, expected < 2s"
        assert stats is not None
        assert stats["total_games"] == 100
    
    def test_random_word_selection_performance(self, test_db_session):
        """Test performance of random word selection"""
        # Create test user
        user = create_test_user(test_db_session, email="randomuser@example.com")
        
        # Create many words
        words = []
        for i in range(1000):
            word = Word(
                text=f"randomword{i}",
                translation=f"случайное{i}",
                description=f"Random description {i}",
                difficulty="easy" if i % 3 == 0 else "medium" if i % 3 == 1 else "hard",
                times_shown=0,
                times_correct=0,
                correct_ratio=0.0
            )
            words.append(word)
        
        test_db_session.add_all(words)
        test_db_session.commit()
        
        # Test random selection performance
        from app.database import get_random_words
        
        start_time = time.time()
        
        # Perform multiple random selections
        for _ in range(20):
            random_words = get_random_words(test_db_session, user.id, count=10)
            assert len(random_words) == 10
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 5.0, f"Random word selection took {duration:.2f}s, expected < 5s"
    
    def test_database_index_performance(self, test_db_session):
        """Test that database indexes are working effectively"""
        # Create test data
        users = []
        for i in range(100):
            user = User(
                name=f"IndexUser {i}",
                email=f"indexuser{i}@example.com",
                password_hash="hashed_password",
                role="user"
            )
            users.append(user)
        
        test_db_session.add_all(users)
        test_db_session.commit()
        
        # Test email index performance
        start_time = time.time()
        user = test_db_session.query(User).filter(User.email == "indexuser50@example.com").first()
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 0.1, f"Email lookup took {duration:.3f}s, expected < 0.1s"
        assert user is not None
        assert user.email == "indexuser50@example.com"
    
    def test_concurrent_database_access(self, test_db_session):
        """Test database performance under concurrent access simulation"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def database_operation(thread_id):
            try:
                # Simulate database operations
                for i in range(10):
                    # Create user
                    user = User(
                        name=f"Thread{thread_id}User{i}",
                        email=f"thread{thread_id}user{i}@example.com",
                        password_hash="hashed_password",
                        role="user"
                    )
                    test_db_session.add(user)
                    test_db_session.commit()
                    
                    # Query user
                    found_user = test_db_session.query(User).filter(
                        User.email == f"thread{thread_id}user{i}@example.com"
                    ).first()
                    
                    assert found_user is not None
                
                results.put(f"Thread {thread_id} completed successfully")
            except Exception as e:
                errors.put(f"Thread {thread_id} error: {str(e)}")
        
        # Start multiple threads
        threads = []
        start_time = time.time()
        
        for thread_id in range(5):
            thread = threading.Thread(target=database_operation, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Check results
        assert errors.qsize() == 0, f"Errors occurred: {list(errors.queue)}"
        assert results.qsize() == 5, "All threads should complete successfully"
        assert duration < 30.0, f"Concurrent operations took {duration:.2f}s, expected < 30s"
    
    def test_large_result_set_performance(self, test_db_session):
        """Test performance when handling large result sets"""
        # Create large dataset
        words = []
        for i in range(2000):
            word = Word(
                text=f"largeword{i}",
                translation=f"большой{i}",
                description=f"Large dataset word {i}",
                difficulty="easy",
                times_shown=i,
                times_correct=i // 2,
                correct_ratio=0.5
            )
            words.append(word)
        
        test_db_session.add_all(words)
        test_db_session.commit()
        
        # Test large query performance
        start_time = time.time()
        all_words = test_db_session.query(Word).filter(Word.difficulty == "easy").all()
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 5.0, f"Large result set query took {duration:.2f}s, expected < 5s"
        assert len(all_words) == 2000
        
        # Test pagination performance
        start_time = time.time()
        paginated_words = test_db_session.query(Word).filter(
            Word.difficulty == "easy"
        ).offset(1000).limit(100).all()
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 1.0, f"Paginated query took {duration:.2f}s, expected < 1s"
        assert len(paginated_words) == 100
    
    def test_database_connection_performance(self, test_db_engine):
        """Test database connection performance"""
        connection_times = []
        
        # Test multiple connections
        for _ in range(10):
            start_time = time.time()
            connection = test_db_engine.connect()
            connection.close()
            end_time = time.time()
            connection_times.append(end_time - start_time)
        
        avg_connection_time = sum(connection_times) / len(connection_times)
        max_connection_time = max(connection_times)
        
        assert avg_connection_time < 0.1, f"Average connection time {avg_connection_time:.3f}s, expected < 0.1s"
        assert max_connection_time < 0.5, f"Max connection time {max_connection_time:.3f}s, expected < 0.5s"