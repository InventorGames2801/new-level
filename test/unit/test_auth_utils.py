"""
Unit tests for authentication utilities
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException, status

from app.auth_utils import get_current_user, get_optional_user, get_admin_user
from app.models import User


@pytest.mark.unit
class TestAuthUtils:
    """Test authentication utility functions"""
    
    def test_get_current_user_valid_session(self, test_db_session, sample_user):
        """Test getting current user with valid session"""
        # Mock request with session
        mock_request = Mock()
        mock_request.session = {"user_id": sample_user.id}
        
        # Call function
        user = get_current_user(mock_request, test_db_session)
        
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    def test_get_current_user_no_session(self, test_db_session):
        """Test getting current user with no session"""
        # Mock request without user_id in session
        mock_request = Mock()
        mock_request.session = {}
        
        # Should raise 401 Unauthorized
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, test_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Unauthorized"
    
    def test_get_current_user_invalid_user_id(self, test_db_session):
        """Test getting current user with invalid user ID"""
        # Mock request with non-existent user_id
        mock_request = Mock()
        mock_request.session = {"user_id": 99999}  # Non-existent ID
        
        # Should raise 401 Unauthorized
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, test_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "User not found"
    
    def test_get_current_user_none_user_id(self, test_db_session):
        """Test getting current user with None user_id"""
        # Mock request with None user_id
        mock_request = Mock()
        mock_request.session = {"user_id": None}
        
        # Should raise 401 Unauthorized
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_request, test_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Unauthorized"
    
    def test_get_optional_user_valid_session(self, test_db_session, sample_user):
        """Test getting optional user with valid session"""
        # Mock request with session
        mock_request = Mock()
        mock_request.session = {"user_id": sample_user.id}
        
        # Call function
        user = get_optional_user(mock_request, test_db_session)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    def test_get_optional_user_no_session(self, test_db_session):
        """Test getting optional user with no session"""
        # Mock request without user_id in session
        mock_request = Mock()
        mock_request.session = {}
        
        # Should return None, not raise exception
        user = get_optional_user(mock_request, test_db_session)
        assert user is None
    
    def test_get_optional_user_invalid_user_id(self, test_db_session):
        """Test getting optional user with invalid user ID"""
        # Mock request with non-existent user_id
        mock_request = Mock()
        mock_request.session = {"user_id": 99999}  # Non-existent ID
        
        # Should return None, not raise exception
        user = get_optional_user(mock_request, test_db_session)
        assert user is None
    
    def test_get_admin_user_valid_admin(self, sample_admin):
        """Test getting admin user with valid admin"""
        admin = get_admin_user(sample_admin)
        
        assert admin.id == sample_admin.id
        assert admin.role == "admin"
    
    def test_get_admin_user_regular_user(self, sample_user):
        """Test getting admin user with regular user"""
        # Should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            get_admin_user(sample_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
        assert "Administrator privileges required" in exc_info.value.detail
    
    def test_get_admin_user_none_role(self, test_db_session):
        """Test getting admin user with user having None role"""
        # Create user with None role
        user = User(
            name="No Role User",
            email="norole@example.com",
            password_hash="hash",
            role=None  # None role
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            get_admin_user(user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_admin_user_empty_role(self, test_db_session):
        """Test getting admin user with user having empty role"""
        # Create user with empty role
        user = User(
            name="Empty Role User",
            email="emptyrole@example.com",
            password_hash="hash",
            role=""  # Empty role
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            get_admin_user(user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_admin_user_case_sensitive(self, test_db_session):
        """Test that admin role check is case sensitive"""
        # Create user with "Admin" (capital A) instead of "admin"
        user = User(
            name="Capital Admin",
            email="capitaladmin@example.com",
            password_hash="hash",
            role="Admin"  # Capital A
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Should raise 403 Forbidden (case sensitive)
        with pytest.raises(HTTPException) as exc_info:
            get_admin_user(user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.parametrize("invalid_role", [
        "user",
        "moderator", 
        "ADMIN",
        "administrator",
        "root",
        "super",
        " admin ",  # with spaces
    ])
    def test_get_admin_user_invalid_roles(self, test_db_session, invalid_role):
        """Test admin check with various invalid roles"""
        user = User(
            name="Invalid Role User",
            email=f"invalid{invalid_role}@example.com",
            password_hash="hash",
            role=invalid_role
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        with pytest.raises(HTTPException) as exc_info:
            get_admin_user(user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN