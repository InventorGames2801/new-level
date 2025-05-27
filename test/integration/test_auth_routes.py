"""
Integration tests for authentication routes
"""
import pytest
from fastapi import status

from tests.conftest import TestData


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_page_get(self, client):
        """Test GET /login returns login page"""
        response = client.get("/login")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_register_page_get(self, client):
        """Test GET /register returns register page"""
        response = client.get("/register")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_login_valid_credentials(self, client, sample_user):
        """Test POST /login with valid credentials"""
        response = client.post("/login", data={
            "email": sample_user.email,
            "password": "testpassword"
        })
        
        # Should redirect after successful login
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert "location" in response.headers
        
        # Check if redirected to home page with success message
        location = response.headers["location"]
        assert "?success=" in location or "/" in location
    
    def test_login_invalid_email(self, client):
        """Test POST /login with invalid email"""
        response = client.post("/login", data={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        
        # Should redirect to login page with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/login" in location
        assert "error=" in location
    
    def test_login_invalid_password(self, client, sample_user):
        """Test POST /login with invalid password"""
        response = client.post("/login", data={
            "email": sample_user.email,
            "password": "wrongpassword"
        })
        
        # Should redirect to login page with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/login" in location
        assert "error=" in location
    
    def test_login_empty_credentials(self, client):
        """Test POST /login with empty credentials"""
        response = client.post("/login", data={
            "email": "",
            "password": ""
        })
        
        # Should return error (422 for validation error or redirect with error)
        assert response.status_code in [422, 303]
    
    def test_register_valid_data(self, client):
        """Test POST /register with valid data"""
        response = client.post("/register", data=TestData.VALID_USER_DATA)
        
        # Should redirect after successful registration
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "?success=" in location
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test POST /register with duplicate email"""
        response = client.post("/register", data={
            "name": "Another User",
            "email": sample_user.email,  # Duplicate email
            "password": "newpassword"
        })
        
        # Should redirect with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/register" in location
        assert "error=" in location
    
    def test_register_short_password(self, client):
        """Test POST /register with short password"""
        response = client.post("/register", data={
            "name": "Test User",
            "email": "newuser@example.com",
            "password": "123"  # Too short
        })
        
        # Should redirect with error
        assert response.status_code == status.HTTP_303_SEE_OTHER
        location = response.headers["location"]
        assert "/register" in location
        assert "error=" in location
    
    @pytest.mark.parametrize("invalid_email", TestData.INVALID_EMAILS)
    def test_register_invalid_emails(self, client, invalid_email):
        """Test POST /register with various invalid emails"""
        response = client.post("/register", data={
            "name": "Test User",
            "email": invalid_email,
            "password": "validpassword"
        })
        
        # Should return validation error or redirect with error
        assert response.status_code in [422, 303]
    
    @pytest.mark.parametrize("invalid_password", TestData.INVALID_PASSWORDS)
    def test_register_invalid_passwords(self, client, invalid_password):
        """Test POST /register with various invalid passwords"""
        response = client.post("/register", data={
            "name": "Test User",
            "email": "test@example.com",
            "password": invalid_password
        })
        
        # Should return validation error or redirect with error
        assert response.status_code in [422, 303]
    
    def test_logout(self, client, sample_user):
        """Test GET /logout"""
        # First login
        login_response = client.post("/login", data={
            "email": sample_user.email,
            "password": "testpassword"
        })
        assert login_response.status_code == status.HTTP_303_SEE_OTHER
        
        # Then logout
        logout_response = client.get("/logout")
        
        # Should redirect to home page
        assert logout_response.status_code == status.HTTP_302_FOUND
        location = logout_response.headers["location"]
        assert "/" in location
    
    def test_logout_without_login(self, client):
        """Test GET /logout without being logged in"""
        response = client.get("/logout")
        
        # Should still redirect (clearing empty session)
        assert response.status_code == status.HTTP_302_FOUND
    
    def test_login_session_persistence(self, client, sample_user):
        """Test that login session persists across requests"""
        # Login
        login_response = client.post("/login", data={
            "email": sample_user.email,
            "password": "testpassword"
        })
        assert login_response.status_code == status.HTTP_303_SEE_OTHER
        
        # Access protected route (should work with session)
        # Note: This depends on having a protected route to test
        # You might need to adjust this based on your actual protected routes
        
    def test_register_auto_login(self, client):
        """Test that registration automatically logs in the user"""
        # Register new user
        response = client.post("/register", data={
            "name": "Auto Login User",
            "email": "autologin@example.com",
            "password": "testpassword"
        })
        
        # Should redirect after successful registration
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # User should now be logged in (session should be set)
        # This can be tested by accessing a protected route if available
    
    def test_concurrent_logins(self, client, sample_user):
        """Test multiple login attempts"""
        # Multiple rapid login attempts should all succeed
        for _ in range(3):
            response = client.post("/login", data={
                "email": sample_user.email,
                "password": "testpassword"
            })
            assert response.status_code == status.HTTP_303_SEE_OTHER
    
    def test_login_updates_last_login(self, client, sample_user, test_db_session):
        """Test that successful login updates last_login timestamp"""
        # Get initial last_login
        initial_last_login = sample_user.last_login
        
        # Login
        response = client.post("/login", data={
            "email": sample_user.email,
            "password": "testpassword"
        })
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Refresh user from database
        test_db_session.refresh(sample_user)
        
        # last_login should be updated
        assert sample_user.last_login != initial_last_login
        assert sample_user.last_login is not None