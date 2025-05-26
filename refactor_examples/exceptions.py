"""
Custom exceptions for better error handling
"""

class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(AppException):
    """Raised when input validation fails"""
    pass

class GameValidationError(ValidationError):
    """Raised when game-specific validation fails"""
    pass

class WordNotFoundError(AppException):
    """Raised when a word is not found"""
    pass

class UserNotFoundError(AppException):
    """Raised when a user is not found"""
    pass

class AuthenticationError(AppException):
    """Raised when authentication fails"""
    pass

class AuthorizationError(AppException):
    """Raised when authorization fails"""
    pass

class DatabaseError(AppException):
    """Raised when database operations fail"""
    pass

class ConfigurationError(AppException):
    """Raised when configuration is invalid"""
    pass