## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Scope**: Single function/method/class
- **Dependencies**: Minimal, mostly mocked
- **Speed**: Fast (< 1s per test)

### Integration Tests
- **Purpose**: Test interaction between components
- **Scope**: Multiple components working together
- **Dependencies**: Real database, HTTP client
- **Speed**: Medium (1-10s per test)

### Performance Tests
- **Purpose**: Verify performance requirements
- **Scope**: System-wide performance metrics
- **Dependencies**: Full system setup
- **Speed**: Slow (10s+ per test)

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Set up test environment
export DATABASE_URL="sqlite:///test.db"
export SECRET_KEY="test_secret_key_for_testing_only_12345678901234567890"
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test category
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m auth           # Authentication tests only
pytest -m game           # Game functionality tests
pytest -m admin          # Admin functionality tests

# Run specific test file
pytest tests/unit/test_models.py
pytest tests/integration/test_auth_routes.py

# Run specific test function
pytest tests/unit/test_models.py::TestUserModel::test_create_user
```

### Test Coverage

```bash
# Run tests with coverage report
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing
```

### Performance Testing

```bash
# Run performance tests (marked as slow)
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Fixtures

### Database Fixtures
- `test_db_engine`: SQLite test database engine
- `test_db_session`: Database session for tests
- `sample_user`: Test user with basic data
- `sample_admin`: Test admin user
- `sample_words`: Collection of test words
- `sample_game_session`: Test game session
- `sample_game_settings`: Game configuration settings

### Authentication Fixtures
- `authenticated_user_session`: HTTP client with logged-in user
- `authenticated_admin_session`: HTTP client with logged-in admin

### HTTP Client Fixtures
- `client`: FastAPI test client
- `app`: FastAPI application instance

## Test Data

### TestData Class
The `TestData` class in `conftest.py` provides constants for testing:

```python
TestData.VALID_USER_DATA        # Valid user registration data
TestData.VALID_WORD_DATA        # Valid word creation data
TestData.VALID_GAME_TYPES       # Supported game types
TestData.INVALID_EMAILS         # Invalid email formats for testing
TestData.INVALID_PASSWORDS      # Invalid passwords for testing
```

### Helper Functions
- `create_test_user()`: Create user with custom parameters
- `create_test_word()`: Create word with custom parameters

## Test Patterns

### Unit Test Pattern
```python
@pytest.mark.unit
class TestClassName:
    def test_function_behavior(self, fixture):
        # Arrange
        input_data = "test_input"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_value
```

### Integration Test Pattern
```python
@pytest.mark.integration
@pytest.mark.auth
class TestAuthRoutes:
    def test_login_valid_credentials(self, client, sample_user):
        # Act
        response = client.post("/login", data={
            "email": sample_user.email,
            "password": "testpassword"
        })
        
        # Assert
        assert response.status_code == 303
        assert "location" in response.headers
```

### Parameterized Test Pattern
```python
@pytest.mark.parametrize("input_value,expected", [
    ("valid_input", True),
    ("invalid_input", False),
])
def test_validation_function(input_value, expected):
    result = validate(input_value)
    assert result == expected
```

## Test Best Practices

### 1. Test Naming
- Use descriptive names: `test_login_with_valid_credentials`
- Follow pattern: `test_[action]_[condition]_[expected_result]`

### 2. Test Organization
- Group related tests in classes
- Use appropriate markers
- Keep tests independent

### 3. Assertions
- Use specific assertions
- Include helpful error messages
- Test both positive and negative cases

### 4. Test Data
- Use fixtures for common data
- Keep test data minimal and focused
- Clean up after tests

### 5. Mocking
- Mock external dependencies
- Don't mock the system under test
- Use appropriate mock types

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=app
      env:
        DATABASE_URL: sqlite:///test.db
        SECRET_KEY: test_secret_key_for_ci_12345678901234567890
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   export DATABASE_URL="sqlite:///test.db"
   ```

2. **Missing Secret Key**
   ```bash
   export SECRET_KEY="test_secret_key_12345678901234567890"
   ```

3. **Import Errors**
   ```bash
   # Run from project root
   cd /path/to/project
   pytest
   ```

4. **Fixture Not Found**
   - Check fixture name spelling
   - Ensure fixture is in conftest.py or imported

### Debug Mode
```bash
# Run with pdb on failure
pytest --pdb

# Run with detailed output
pytest -vvv

# Run with print statements
pytest -s
```

## Test Metrics

### Coverage Goals
- Unit Tests: > 95% coverage
- Integration Tests: > 80% coverage
- Overall: > 90% coverage

### Performance Benchmarks
- Unit tests: < 1s each
- Integration tests: < 10s each
- Full test suite: < 5 minutes

### Quality Metrics
- All tests should be deterministic
- No test dependencies
- Clear, descriptive test names
- Comprehensive edge case coverage