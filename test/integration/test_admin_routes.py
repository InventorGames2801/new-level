"""
Integration tests for admin routes
"""
import pytest
from fastapi import status

from tests.conftest import TestData


@pytest.mark.integration
@pytest.mark.admin
class TestAdminRoutes:
    """Test admin-related routes"""
    
    def test_admin_dashboard_authenticated(self, authenticated_admin_session, sample_game_settings):
        """Test GET /admin with authenticated admin"""
        response = authenticated_admin_session.get("/admin")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_admin_dashboard_regular_user(self, authenticated_user_session):
        """Test GET /admin with regular user"""
        response = authenticated_user_session.get("/admin")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_dashboard_unauthenticated(self, client):
        """Test GET /admin without authentication"""
        response = client.get("/admin")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_dictionary_authenticated(self, authenticated_admin_session, sample_words):
        """Test GET /admin/dictionary with authenticated admin"""
        response = authenticated_admin_session.get("/admin/dictionary")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_admin_dictionary_regular_user(self, authenticated_user_session):
        """Test GET /admin/dictionary with regular user"""
        response = authenticated_user_session.get("/admin/dictionary")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_users_authenticated(self, authenticated_admin_session, sample_user):
        """Test GET /admin/users with authenticated admin"""
        response = authenticated_admin_session.get("/admin/users")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_admin_users_with_pagination(self, authenticated_admin_session, sample_user):
        """Test GET /admin/users with pagination parameters"""
        response = authenticated_admin_session.get("/admin/users?page=1&per_page=5")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_admin_users_invalid_pagination(self, authenticated_admin_session):
        """Test GET /admin/users with invalid pagination"""
        response = authenticated_admin_session.get("/admin/users?page=0")  # Invalid page
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_word_valid(self, authenticated_admin_session):
        """Test POST /admin/words/create with valid data"""
        response = authenticated_admin_session.post("/admin/words/create", data={
            "text": "newword",
            "translation": "новоеслово",
            "description": "a new word for testing",
            "difficulty": "medium"
        })
        
        # Should redirect to dictionary
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "/admin/dictionary" in response.headers["location"]
    
    def test_create_word_invalid_data(self, authenticated_admin_session):
        """Test POST /admin/words/create with invalid data"""
        response = authenticated_admin_session.post("/admin/words/create", data={
            "text": "",  # Empty text
            "translation": "перевод",
            "description": "description",
            "difficulty": "easy"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_word_invalid_difficulty(self, authenticated_admin_session):
        """Test POST /admin/words/create with invalid difficulty"""
        response = authenticated_admin_session.post("/admin/words/create", data={
            "text": "testword",
            "translation": "тестслово",
            "description": "test description",
            "difficulty": "invalid"  # Invalid difficulty
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_word_regular_user(self, authenticated_user_session):
        """Test POST /admin/words/create with regular user"""
        response = authenticated_user_session.post("/admin/words/create", data=TestData.VALID_WORD_DATA)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_word_valid(self, authenticated_admin_session, sample_words):
        """Test POST /admin/words/{word_id}/edit with valid data"""
        word = sample_words[0]
        
        response = authenticated_admin_session.post(f"/admin/words/{word.id}/edit", data={
            "text": "updated_word",
            "translation": "обновленноеслово",
            "description": "updated description",
            "difficulty": "hard"
        })
        
        # Should redirect to dictionary
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "/admin/dictionary" in response.headers["location"]
    
    def test_update_word_nonexistent(self, authenticated_admin_session):
        """Test POST /admin/words/{word_id}/edit with nonexistent word"""
        response = authenticated_admin_session.post("/admin/words/99999/edit", data={
            "text": "updated_word",
            "translation": "обновленноеслово",
            "description": "updated description",
            "difficulty": "medium"
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_word_invalid_data(self, authenticated_admin_session, sample_words):
        """Test POST /admin/words/{word_id}/edit with invalid data"""
        word = sample_words[0]
        
        response = authenticated_admin_session.post(f"/admin/words/{word.id}/edit", data={
            "text": "",  # Empty text
            "translation": "перевод",
            "description": "description",
            "difficulty": "easy"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_word_valid(self, authenticated_admin_session, sample_words):
        """Test POST /admin/words/{word_id}/delete with valid word"""
        word = sample_words[0]
        
        response = authenticated_admin_session.post(f"/admin/words/{word.id}/delete")
        
        # Should redirect to dictionary
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "/admin/dictionary" in response.headers["location"]
    
    def test_delete_word_nonexistent(self, authenticated_admin_session):
        """Test POST /admin/words/{word_id}/delete with nonexistent word"""
        response = authenticated_admin_session.post("/admin/words/99999/delete")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_word_regular_user(self, authenticated_user_session, sample_words):
        """Test POST /admin/words/{word_id}/delete with regular user"""
        word = sample_words[0]
        
        response = authenticated_user_session.post(f"/admin/words/{word.id}/delete")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_user_valid(self, authenticated_admin_session):
        """Test POST /admin/users/create with valid data"""
        response = authenticated_admin_session.post("/admin/users/create", data={
            "name": "New Admin User",
            "email": "newadmin@example.com",
            "password": "adminpassword",
            "role": "admin"
        })
        
        # Should redirect to users page
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "/admin/users" in response.headers["location"]
    
    def test_create_user_duplicate_email(self, authenticated_admin_session, sample_user):
        """Test POST /admin/users/create with duplicate email"""
        response = authenticated_admin_session.post("/admin/users/create", data={
            "name": "Duplicate User",
            "email": sample_user.email,  # Duplicate email
            "password": "password",
            "role": "user"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_user_regular_user(self, authenticated_user_session):
        """Test POST /admin/users/create with regular user"""
        response = authenticated_user_session.post("/admin/users/create", data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password",
            "role": "user"
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_user_valid(self, authenticated_admin_session, sample_user):
        """Test POST /admin/users/{user_id}/delete with valid user"""
        response = authenticated_admin_session.post(f"/admin/users/{sample_user.id}/delete")
        
        # Should redirect to users page
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "/admin/users" in response.headers["location"]
    
    def test_delete_user_self(self, authenticated_admin_session, sample_admin):
        """Test POST /admin/users/{user_id}/delete attempting to delete self"""
        response = authenticated_admin_session.post(f"/admin/users/{sample_admin.id}/delete")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_user_nonexistent(self, authenticated_admin_session):
        """Test POST /admin/users/{user_id}/delete with nonexistent user"""
        response = authenticated_admin_session.post("/admin/users/99999/delete")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_toggle_admin_role_valid(self, authenticated_admin_session, sample_user):
        """Test POST /admin/users/{user_id}/toggle_admin_role with valid user"""
        response = authenticated_admin_session.post(f"/admin/users/{sample_user.id}/toggle_admin_role")
        
        # Should redirect to users page with success
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/admin/users" in location
        assert "success=" in location
    
    def test_toggle_admin_role_self(self, authenticated_admin_session, sample_admin):
        """Test POST /admin/users/{user_id}/toggle_admin_role attempting to change own role"""
        response = authenticated_admin_session.post(f"/admin/users/{sample_admin.id}/toggle_admin_role")
        
        # Should redirect with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/admin/users" in location
        assert "error=" in location
    
    def test_toggle_admin_role_nonexistent(self, authenticated_admin_session):
        """Test POST /admin/users/{user_id}/toggle_admin_role with nonexistent user"""
        response = authenticated_admin_session.post("/admin/users/99999/toggle_admin_role")
        
        # Should redirect with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/admin/users" in location
        assert "error=" in location
    
    def test_update_settings_valid(self, authenticated_admin_session, sample_game_settings):
        """Test POST /admin/settings/update with valid settings"""
        response = authenticated_admin_session.post("/admin/settings/update", data={
            "setting_points_per_answer": "15",
            "setting_daily_experience_limit": "250"
        })
        
        # Should redirect with success
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/admin/settings" in location
        assert "success=" in location
    
    def test_update_settings_regular_user(self, authenticated_user_session):
        """Test POST /admin/settings/update with regular user"""
        response = authenticated_user_session.post("/admin/settings/update", data={
            "setting_points_per_answer": "15"
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_routes_require_admin_role(self, authenticated_user_session):
        """Test that all admin routes require admin role"""
        admin_routes = [
            "/admin",
            "/admin/dictionary",
            "/admin/users"
        ]
        
        for route in admin_routes:
            response = authenticated_user_session.get(route)
            assert response.status_code == status.HTTP_403_FORBIDDEN, f"Route {route} should require admin role"
    
    def test_admin_post_routes_require_admin_role(self, authenticated_user_session):
        """Test that admin POST routes require admin role"""
        admin_post_routes = [
            ("/admin/words/create", {"text": "test", "translation": "тест", "description": "test", "difficulty": "easy"}),
            ("/admin/users/create", {"name": "Test", "email": "test@test.com", "password": "test", "role": "user"}),
            ("/admin/settings/update", {"setting_test": "value"})
        ]
        
        for route, data in admin_post_routes:
            response = authenticated_user_session.post(route, data=data)
            assert response.status_code == status.HTTP_403_FORBIDDEN, f"Route {route} should require admin role"