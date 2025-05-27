"""
Unit tests for configuration
"""
import pytest
import os
from unittest.mock import patch

from app.config import Settings


@pytest.mark.unit
class TestConfig:
    """Test application configuration"""
    
    def test_default_values(self):
        """Test default configuration values"""
        # Test with minimal required environment
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890'
        }, clear=True):
            settings = Settings()
            
            assert settings.PROJECT_NAME == "FastAPI Demo App"
            assert settings.ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.DEBUG is False
            assert settings.INIT_DB is False
    
    def test_environment_override(self):
        """Test that environment variables override defaults"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test',
            'SECRET_KEY': 'custom_secret_key_12345678901234567890',
            'PROJECT_NAME': 'Custom App Name',
            'DEBUG': 'true',
            'INIT_DB': 'true',
            'ACCESS_TOKEN_EXPIRE_MINUTES': '60'
        }, clear=True):
            settings = Settings()
            
            assert settings.PROJECT_NAME == "Custom App Name"
            assert settings.DATABASE_URL == "postgresql://test"
            assert settings.SECRET_KEY == "custom_secret_key_12345678901234567890"
            assert settings.DEBUG is True
            assert settings.INIT_DB is True
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    
    def test_boolean_parsing(self):
        """Test boolean environment variable parsing"""
        # Test various boolean values
        boolean_tests = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('', False),
        ]
        
        for env_value, expected in boolean_tests:
            with patch.dict(os.environ, {
                'DATABASE_URL': 'sqlite:///test.db',
                'SECRET_KEY': 'test_secret_key_12345678901234567890',
                'DEBUG': env_value
            }, clear=True):
                settings = Settings()
                assert settings.DEBUG == expected, f"Failed for value: {env_value}"
    
    def test_integer_parsing(self):
        """Test integer environment variable parsing"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890',
            'ACCESS_TOKEN_EXPIRE_MINUTES': '120'
        }, clear=True):
            settings = Settings()
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
            assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    
    def test_string_stripping(self):
        """Test that string values are stripped of whitespace"""
        with patch.dict(os.environ, {
            'DATABASE_URL': '  sqlite:///test.db  ',
            'SECRET_KEY': '  test_secret_key_12345678901234567890  ',
            'PROJECT_NAME': '  Spaced App Name  '
        }, clear=True):
            settings = Settings()
            
            assert settings.DATABASE_URL == "sqlite:///test.db"
            assert settings.SECRET_KEY == "test_secret_key_12345678901234567890"
            assert settings.PROJECT_NAME == "Spaced App Name"
    
    def test_case_sensitivity(self):
        """Test that environment variables are case sensitive"""
        with patch.dict(os.environ, {
            'database_url': 'sqlite:///lowercase.db',  # lowercase
            'DATABASE_URL': 'sqlite:///uppercase.db',  # uppercase
            'SECRET_KEY': 'test_secret_key_12345678901234567890'
        }, clear=True):
            settings = Settings()
            
            # Should use uppercase version
            assert settings.DATABASE_URL == "sqlite:///uppercase.db"
    
    def test_missing_required_fields(self):
        """Test behavior with missing required fields"""
        # Test with missing DATABASE_URL
        with patch.dict(os.environ, {
            'SECRET_KEY': 'test_secret_key_12345678901234567890'
        }, clear=True):
            with pytest.raises(Exception):  # Should raise validation error
                Settings()
        
        # Test with missing SECRET_KEY
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db'
        }, clear=True):
            with pytest.raises(Exception):  # Should raise validation error
                Settings()
    
    def test_extra_fields_allowed(self):
        """Test that extra environment variables are allowed"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890',
            'EXTRA_FIELD': 'extra_value',
            'ANOTHER_FIELD': 'another_value'
        }, clear=True):
            # Should not raise error even with extra fields
            settings = Settings()
            assert settings.DATABASE_URL == "sqlite:///test.db"
    
    @pytest.mark.parametrize("invalid_value", [
        "not_a_number",
        "12.5",  # Float instead of int
        "",
        "   ",  # Whitespace only
    ])
    def test_invalid_integer_values(self, invalid_value):
        """Test handling of invalid integer values"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890',
            'ACCESS_TOKEN_EXPIRE_MINUTES': invalid_value
        }, clear=True):
            with pytest.raises(Exception):  # Should raise validation error
                Settings()
    
    def test_environment_file_loading(self, tmp_path):
        """Test loading from .env file"""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
DATABASE_URL=sqlite:///from_file.db
SECRET_KEY=file_secret_key_12345678901234567890
PROJECT_NAME=App From File
DEBUG=true
        """.strip())
        
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Clear environment variables
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings()
                
                assert settings.DATABASE_URL == "sqlite:///from_file.db"
                assert settings.SECRET_KEY == "file_secret_key_12345678901234567890"
                assert settings.PROJECT_NAME == "App From File"
                assert settings.DEBUG is True
        finally:
            os.chdir(original_cwd)
    
    def test_environment_override_file(self, tmp_path):
        """Test that environment variables override .env file"""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
DATABASE_URL=sqlite:///from_file.db
SECRET_KEY=file_secret_key_12345678901234567890
PROJECT_NAME=App From File
        """.strip())
        
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Set environment variable that should override file
            with patch.dict(os.environ, {
                'PROJECT_NAME': 'App From Environment'
            }):
                settings = Settings()
                
                # File values
                assert settings.DATABASE_URL == "sqlite:///from_file.db"
                assert settings.SECRET_KEY == "file_secret_key_12345678901234567890"
                
                # Environment override
                assert settings.PROJECT_NAME == "App From Environment"
        finally:
            os.chdir(original_cwd)
    
    def test_settings_immutability(self):
        """Test that settings are immutable after creation"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890'
        }, clear=True):
            settings = Settings()
            
            # Attempting to modify should raise an error (if validate_assignment is True)
            with pytest.raises(Exception):
                settings.DATABASE_URL = "modified://url"
    
    def test_settings_repr(self):
        """Test settings string representation doesn't expose secrets"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test_secret_key_12345678901234567890'
        }, clear=True):
            settings = Settings()
            settings_str = str(settings)
            
            # SECRET_KEY should not appear in string representation
            assert 'test_secret_key' not in settings_str