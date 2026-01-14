# Data Provider Examples

This directory contains comprehensive examples demonstrating how to use the Data Retrieval Module with different data sources.

## 📁 File Structure

```
examples/
├── README.md                    # This file
├── rest_api_example.py          # REST API provider examples
├── database_example.py          # Database provider examples
└── comprehensive_example.py     # Unified multi-provider example
```

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install data-retrieval-module

# With REST API support
pip install data-retrieval-module

# With database support
pip install data-retrieval-module[database]

# With async support
pip install data-retrieval-module[async]

# All features
pip install data-retrieval-module[all]
```

## 📡 REST API Examples

### Synchronous REST API Usage

```python
from data_retrieval import RestDataProvider

# Create provider
provider = RestDataProvider(
    base_url="https://jsonplaceholder.typicode.com",
    headers={"Content-Type": "application/json"},
    timeout=10.0
)

# Use with context manager
with provider.connection():
    # GET request
    users = provider.fetch(endpoint="/users")
    print(f"Found {len(users.data)} users")
    
    # POST request
    new_user = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    result = provider.fetch(
        endpoint="/users",
        method="POST",
        data=new_user
    )
```

### Asynchronous REST API Usage

```python
import asyncio
from data_retrieval import AsyncRestDataProvider

async def fetch_data():
    provider = AsyncRestDataProvider(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"Content-Type": "application/json"}
    )
    
    async with provider.async_connection():
        # Fetch multiple endpoints concurrently
        endpoints = ["/users", "/posts", "/comments"]
        results = await provider.fetch_multiple(endpoints)
        
        for endpoint, result in zip(endpoints, results):
            print(f"{endpoint}: {len(result.data)} items")

# Run the async function
asyncio.run(fetch_data())
```

### Run REST API Examples

```bash
python examples/rest_api_example.py
```

## 🗄️ Database Examples

### SQLite Database Usage

```python
from data_retrieval import DatabaseProvider, DatabaseConfig

# Configure database
config = DatabaseConfig(
    database_type='sqlite',
    database='myapp.db'
)

# Create provider
provider = DatabaseProvider(config)

# Use with context manager
with provider.connection():
    # Execute queries
    users = provider.fetch("SELECT * FROM users")
    
    # Execute statements
    provider.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        params=['Alice', 'alice@example.com']
    )
    
    # Use transactions
    with provider.transaction():
        provider.execute("UPDATE users SET name = ? WHERE id = ?", ['Bob', 1])
        provider.execute("DELETE FROM users WHERE active = ?", [False])
```

### PostgreSQL Database Usage

```python
from data_retrieval import DatabaseProvider, DatabaseConfig

# Configure PostgreSQL
config = DatabaseConfig(
    database_type='postgres',
    host='localhost',
    port=5432,
    database='myapp',
    username='postgres',
    password='password'
)

provider = DatabaseProvider(config)

with provider.connection():
    # Use PostgreSQL-specific syntax
    users = provider.fetch("SELECT * FROM users WHERE active = $1", params=[True])
```

### Asynchronous Database Usage

```python
import asyncio
from data_retrieval import AsyncDatabaseProvider, DatabaseConfig

async def async_db_example():
    config = DatabaseConfig(
        database_type='sqlite',
        database='async_app.db'
    )
    
    provider = AsyncDatabaseProvider(config)
    
    async with provider.async_connection():
        users = await provider.fetch("SELECT * FROM users")
        print(f"Found {len(users.data)} users")

asyncio.run(async_db_example())
```

### Run Database Examples

```bash
python examples/database_example.py
```

## 🔄 Comprehensive Multi-Provider Example

The comprehensive example demonstrates how to use multiple data providers together in a unified application:

```python
from data_retrieval import (
    RestDataProvider, AsyncRestDataProvider,
    DatabaseProvider, AsyncDatabaseProvider,
    DatabaseConfig
)

class UnifiedDataProcessor:
    def __init__(self):
        # Initialize multiple providers
        self.api_provider = RestDataProvider(
            base_url="https://api.example.com"
        )
        
        self.db_provider = DatabaseProvider(
            DatabaseConfig(database_type='sqlite', database='app.db')
        )
    
    def sync_data(self):
        # Fetch from API and store in database
        with self.api_provider.connection():
            data = self.api_provider.fetch("/users")
        
        with self.db_provider.connection():
            for user in data.data:
                self.db_provider.execute(
                    "INSERT INTO users VALUES (?, ?, ?)",
                    params=[user['id'], user['name'], user['email']]
                )
```

### Run Comprehensive Example

```bash
python examples/comprehensive_example.py
```

## 🛠️ Advanced Features

### Custom Validation

```python
def validate_user(user_data):
    required_fields = ['id', 'name', 'email']
    return all(field in user_data for field in required_fields)

provider.validate = validate_user
```

### Custom Transformation

```python
def transform_user(user_data):
    transformed = user_data.copy()
    transformed['full_name'] = f"{user_data['first_name']} {user_data['last_name']}"
    return transformed

provider.transform = transform_user
```

### Error Handling

```python
from data_retrieval.model.exceptions import ConnectionError, QueryError

try:
    with provider.connection():
        result = provider.fetch("/data")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except QueryError as e:
    print(f"Query failed: {e}")
```

### Retry Logic

```python
def unreliable_operation():
    # This might fail sometimes
    return provider.fetch("/unstable-endpoint")

result = provider.with_retry(
    unreliable_operation,
    max_retries=3,
    retry_delay=1.0,
    parameters={}
)
```

## 📊 Supported Data Sources

### REST APIs
- ✅ JSONPlaceholder
- ✅ GitHub API
- ✅ Custom REST APIs
- ✅ Authentication headers
- ✅ Custom request methods
- ✅ Query parameters

### Databases
- ✅ SQLite (built-in)
- ✅ PostgreSQL (requires `psycopg2-binary`)
- ✅ MySQL (requires `PyMySQL`)
- ✅ Async SQLite (requires `aiosqlite`)
- ✅ Async PostgreSQL (requires `asyncpg`)

## 🔧 Configuration

### Environment Variables

```bash
# Database configuration
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=myapp
export DB_USER=postgres
export DB_PASSWORD=password

# API configuration
export API_BASE_URL=https://api.example.com
export API_TOKEN=your-api-token
```

### Configuration Files

```python
# config.py
DATABASE_CONFIG = DatabaseConfig(
    database_type='postgres',
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME', 'myapp'),
    username=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'password')
)

API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'https://api.example.com'),
    'headers': {
        'Authorization': f"Bearer {os.getenv('API_TOKEN', '')}",
        'Content-Type': 'application/json'
    },
    'timeout': 30.0
}
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific provider tests
pytest tests/test_rest_provider.py
pytest tests/test_database_provider.py

# Run with coverage
pytest --cov=data_retrieval --cov-report=html
```

### Test Examples

Each example file includes comprehensive test cases that demonstrate:

- ✅ Connection management
- ✅ Data fetching and transformation
- ✅ Error handling
- ✅ Retry logic
- ✅ Async operations
- ✅ Custom validation

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [API Reference](../docs/api.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

## 🤝 Contributing

We welcome contributions! Please see the [Contributing Guide](../CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Happy coding! 🚀**
