# Data Retrieval Module Tests

This directory contains comprehensive unit tests for the Data Retrieval Module, including tests for both synchronous and asynchronous data providers.

## Test Structure

### Files
- `test_data_provider.py` - Main test suite for DataProvider and AsyncDataProvider
- `test_config.py` - Test configuration and utilities
- `conftest.py` - Pytest fixtures and configuration
- `__init__.py` - Tests package initialization

### Test Coverage

#### DataProvider Tests
- ✅ Initialization and configuration
- ✅ Connection management (connect/disconnect)
- ✅ Context managers
- ✅ Data fetching with filters
- ✅ Error handling and exceptions
- ✅ Retry logic
- ✅ Hook methods (validate, transform, health_check)
- ✅ Utility methods (fetch_or_raise, with_retry)

#### AsyncDataProvider Tests
- ✅ All DataProvider functionality in async context
- ✅ Async context managers
- ✅ Async/await patterns
- ✅ Async retry logic
- ✅ Async iteration and streaming

#### QueryResult Tests
- ✅ Data container functionality
- ✅ Empty result handling
- ✅ Metadata support

#### Integration Tests
- ✅ Provider inheritance
- ✅ Exception hierarchy
- ✅ Cross-component interaction

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Basic Test Commands
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_data_provider.py

# Run specific test method
pytest tests/test_data_provider.py::TestDataProvider::test_connect_success
```

### Using Makefile
```bash
# Install dependencies
make install

# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run async tests only
make test-async

# Run tests with coverage
make test-coverage

# Run all test suites with coverage
make test-all

# Format code and run tests
make dev-test
```

### Test Categories

#### Unit Tests
```bash
pytest tests/ -m "unit"
```
Fast, isolated tests that don't require external dependencies.

#### Integration Tests
```bash
pytest tests/ -m "integration"
```
Tests that verify interaction between components.

#### Async Tests
```bash
pytest tests/ -m "async_test"
```
Tests for asynchronous functionality.

### Coverage Reports
```bash
# Generate HTML coverage report
pytest tests/ --cov=data_retrieval --cov-report=html

# View coverage in terminal
pytest tests/ --cov=data_retrieval --cov-report=term

# Generate XML coverage (for CI)
pytest tests/ --cov=data_retrieval --cov-report=xml
```

## Test Configuration

### Environment Variables
```bash
# Database configuration
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=test_db
export TEST_DB_USER=test_user
export TEST_DB_PASSWORD=test_pass

# API configuration
export TEST_API_URL=http://localhost:8000
export TEST_API_TIMEOUT=30
export TEST_API_KEY=test_key

# Logging
export TEST_LOG_LEVEL=DEBUG
```

### Pytest Configuration
Configuration is in `pytest.ini`:
- Test discovery patterns
- Output formatting
- Markers for test categorization
- Warning filters

## Mock Objects

### TestUser Class
Simple test data class used throughout tests:
```python
class TestUser:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
```

### Mock Providers
- `MockDataProvider` - Synchronous provider for testing
- `MockAsyncDataProvider` - Asynchronous provider for testing
- Configurable failure scenarios for error testing

## Fixtures

### Pytest Fixtures
- `sample_data` - Sample test data
- `mock_logger` - Mock logger instance
- `sync_data_provider` - Synchronous provider instance
- `async_data_provider` - Asynchronous provider instance
- `mock_query_result` - Mock QueryResult instance

### Usage Example
```python
def test_with_fixture(sync_data_provider):
    result = sync_data_provider.fetch()
    assert len(result.data) > 0
```

## Test Patterns

### AAA Pattern (Arrange, Act, Assert)
```python
def test_connect_success(self):
    # Arrange
    provider = MockDataProvider()
    
    # Act
    provider.connect()
    
    # Assert
    self.assertEqual(provider.get_provider_status(), ProviderStatus.CONNECTED)
```

### Mock Testing
```python
def test_with_retry_success(self):
    # Arrange
    operation = MagicMock(return_value="success")
    provider = MockDataProvider()
    
    # Act
    result = provider.with_retry(operation)
    
    # Assert
    self.assertEqual(result, "success")
    operation.assert_called_once()
```

### Async Testing
```python
async def test_async_fetch_data(self):
    # Arrange
    provider = MockAsyncDataProvider()
    
    # Act
    result = await provider.fetch()
    
    # Assert
    self.assertIsInstance(result, QueryResult)
    self.assertEqual(len(result.data), 3)
```

## Best Practices

### Test Naming
- Use descriptive test names
- Follow `test_what_should_happen_when` pattern
- Group related tests in classes

### Test Organization
- Separate unit and integration tests
- Use fixtures for common setup
- Keep tests focused and independent

### Error Testing
- Test both success and failure scenarios
- Verify exception types and messages
- Test edge cases and boundary conditions

### Async Testing
- Use `unittest.IsolatedAsyncioTestCase` for async tests
- Properly await all async operations
- Test async context managers and iterators

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run tests
        run: make test-all
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Async Test Issues
- Use `pytest-asyncio` plugin
- Ensure proper event loop handling
- Use `AsyncMock` for async functions

#### Mock Issues
- Use `MagicMock` for regular methods
- Use `AsyncMock` for async methods
- Verify mock calls with appropriate assertions

### Debugging Tests
```bash
# Run with debugger
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l

# Run specific test with verbose output
pytest tests/test_data_provider.py::TestDataProvider::test_connect_success -v -s
```
