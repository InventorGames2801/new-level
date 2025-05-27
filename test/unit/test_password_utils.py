"""
Unit tests for password utilities
"""
import pytest
from app.password_utils import get_password_hash, verify_password


@pytest.mark.unit
class TestPasswordUtils:
    """Test password utility functions"""
    
    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password  # Hash should be different from original
        assert len(hashed) > 0
        assert isinstance(hashed, str)
    
    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes (due to salt)"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "correctpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        correct_password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(correct_password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_verify_password_none(self):
        """Test password verification with None values"""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        # This should not raise an exception
        assert verify_password(None, hashed) is False
    
    def test_hash_empty_password(self):
        """Test hashing empty password"""
        hashed = get_password_hash("")
        
        assert hashed is not None
        assert len(hashed) > 0
        assert verify_password("", hashed) is True
    
    def test_hash_special_characters(self):
        """Test hashing password with special characters"""
        password = "пароль!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed) is True
    
    def test_hash_long_password(self):
        """Test hashing very long password"""
        password = "a" * 1000  # 1000 character password
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed) is True
    
    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters"""
        password = "测试密码🔒🛡️"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed) is True
    
    def test_verify_malformed_hash(self):
        """Test verification with malformed hash"""
        password = "testpassword"
        malformed_hash = "not_a_valid_hash"
        
        # Should return False, not raise exception
        assert verify_password(password, malformed_hash) is False
    
    @pytest.mark.parametrize("password", [
        "simple",
        "Complex123!",
        "verylongpasswordwithmanycharacters",
        "123456789",
        "!@#$%^&*()",
        "пароль",
        "パスワード",
        "كلمة المرور"
    ])
    def test_various_passwords(self, password):
        """Test hashing and verification with various password types"""
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "wrong", hashed) is False