# Data Retrieval Module

A standardized interface for data providers with both synchronous and asynchronous support. This module provides abstract base classes that enable consistent data retrieval patterns across different data sources (APIs, databases, files, etc.).

## Features

- 🔄 **Dual API Support**: Both sync and async interfaces
- 🏗️ **Abstract Base Classes**: Standardized patterns for data providers
- 🔌 **Connection Management**: Built-in connection handling with context managers
- 🔄 **Retry Logic**: Automatic retry with configurable parameters
- 📊 **Pagination Support**: Standardized pagination with QueryResult
- 🎣 **Hook Methods**: Customizable validation and transformation
- 🧪 **Type Safety**: Full type hints and generic support
- ✅ **Well Tested**: Comprehensive unit test coverage

## Installation

### Basic Installation
```bash
pip install data-retrieval-module
```

### With Async Support
```bash
pip install data-retrieval-module[async]
```

### Development Installation
```bash
pip install data-retrieval-module[dev]
```

### All Features
```bash
pip install data-retrieval-module[all]
```

## Quick Start

### Synchronous Data Provider

```python
from data_retrieval import DataProvider, QueryResult
from data_retrieval.model import ProviderStatus

class UserProvider(DataProvider[User]):
    def _connect(self) -> None:
        self._db = Database.connect(...)
    
    def _disconnect(self) -> None:
        self._db.close()
    
    def fetch(self, *args, **kwargs) -> QueryResult[User]:
        filters = kwargs.get("filters", {})
        users = self._db.users.find(filters)
        return QueryResult(
            data=users,
            total_count=len(users),
            metadata={"source": "database"}
        )

# Usage
provider = UserProvider()
with provider.connection(host="localhost", port=5432):
    result = provider.fetch(filters={"active": True})
    for user in result.data:
        print(user.name)
```

### Asynchronous Data Provider

```python
from data_retrieval import AsyncDataProvider

class AsyncUserProvider(AsyncDataProvider[User]):
    async def _connect(self) -> None:
        self._db = await Database.connect(...)
    
    async def _disconnect(self) -> None:
        await self._db.close()
    
    async def fetch(self, *args, **kwargs) -> QueryResult[User]:
        filters = kwargs.get("filters", {})
        users = await self._db.users.find(filters)
        return QueryResult(
            data=users,
            total_count=len(users),
            metadata={"source": "database"}
        )

# Usage
async def main():
    provider = AsyncUserProvider()
    async with provider.async_connection(host="localhost", port=5432) as p:
        result = await p.fetch(filters={"active": True})
        for user in result.data:
            print(user.name)
```

## Core Classes

### DataProvider (Synchronous)

Abstract base class for synchronous data providers.

**Key Methods:**
- `connect(**config)` - Establish connection
- `disconnect()` - Close connection
- `fetch(*args, **kwargs)` - Retrieve data
- `fetch_or_raise(*args, **kwargs)` - Fetch with error handling
- `with_retry(operation, max_retries, retry_delay)` - Retry logic

**Hook Methods:**
- `validate(data)` - Validate data
- `transform(data)` - Transform data
- `health_check()` - Health status

### AsyncDataProvider (Asynchronous)

Abstract base class for asynchronous data providers.

**Key Methods:**
- `async connect(**config)` - Establish connection
- `async disconnect()` - Close connection
- `async fetch(*args, **kwargs)` - Retrieve data
- `async fetch_or_raise(*args, **kwargs)` - Fetch with error handling
- `async with_retry(operation, max_retries, retry_delay)` - Retry logic

### QueryResult

Standardized container for query results.

```python
@dataclass
class QueryResult[T]:
    data: List[T]
    total_count: int
    metadata: Dict[str, Any]
    
    def is_empty(self) -> bool:
        return self.total_count == 0
```

## Advanced Usage

### Custom Validation

```python
class ValidatedProvider(DataProvider[User]):
    def validate(self, data: User) -> bool:
        # Custom validation logic
        return data.email and "@" in data.email
```

### Data Transformation

```python
class TransformingProvider(DataProvider[User]):
    def transform(self, data: dict) -> User:
        # Convert raw data to User object
        return User(**data)
```

### Retry Logic

```python
provider = MyProvider()

# Retry with custom parameters
result = provider.with_retry(
    operation=lambda: provider.fetch(filters={"id": "123"}),
    max_retries=5,
    retry_delay=2.0,
    parameters={}
)
```

### Context Managers

```python
# Automatic connection management
with provider.connection(host="localhost") as p:
    data = p.fetch()

# Async version
async with provider.async_connection(host="localhost") as p:
    data = await p.fetch()
```

## Error Handling

The module provides specific exception types:

```python
from data_retrieval.model.exceptions import (
    DataProviderError,
    ConnectionError,
    QueryError,
    ValidationError
)

try:
    result = provider.fetch(filters={"invalid": "field"})
except ConnectionError as e:
    print(f"Connection failed: {e}")
except QueryError as e:
    print(f"Query failed: {e}")
except DataProviderError as e:
    print(f"General error: {e}")
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/AbigailWilliams1692/data-retrieval-module.git
cd data-retrieval-module

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=data_retrieval --cov-report=html

# Run specific test file
pytest tests/test_data_provider.py
```

### Code Quality

```bash
# Format code
black data_retrieval/ tests/

# Sort imports
isort data_retrieval/ tests/

# Type checking
mypy data_retrieval/

# Linting
flake8 data_retrieval/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- 📖 [Documentation](https://github.com/AbigailWilliams1692/data-retrieval-module/wiki)
- 🐛 [Bug Reports](https://github.com/AbigailWilliams1692/data-retrieval-module/issues)
- 💬 [Discussions](https://github.com/AbigailWilliams1692/data-retrieval-module/discussions)

## Related Projects

- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - SQL toolkit and ORM
- [Django ORM](https://github.com/django/django) - Django's database ORM
- [Tortoise ORM](https://github.com/tortoise/tortoise-orm) - Async ORM for Python

---

**Made with ❤️ by [AbigailWilliams1692](https://github.com/AbigailWilliams1692)**
