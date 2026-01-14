#######################################################################
# Project: Data Retrieval Module
# File: db_provider.py
# Description: Database data provider implementations
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass

# Third-party Packages
try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import asyncpg
    ASYNC_POSTGRES_AVAILABLE = True
except ImportError:
    ASYNC_POSTGRES_AVAILABLE = False

try:
    import aiosqlite
    ASYNC_SQLITE_AVAILABLE = True
except ImportError:
    ASYNC_SQLITE_AVAILABLE = False

# Local Packages
from data_retrieval.model.data_provider import DataProvider, AsyncDataProvider
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import ConnectionError, QueryError, ValidationError


#######################################################################
# Database Configuration
#######################################################################
@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    database_type: str  # 'sqlite', 'postgres', 'mysql'
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    connection_timeout: int = 30
    pool_size: Optional[int] = None


#######################################################################
# Database Data Provider (Synchronous)
#######################################################################
class Database_DataProvider(DataProvider[Any]):
    """
    Synchronous database data provider.
    
    Provides standardized interface for interacting with SQL databases.
    Supports SQLite, PostgreSQL, and MySQL with automatic connection management.
    
    Example Usage:
        config = DatabaseConfig(
            database_type='postgres',
            host='localhost',
            database='mydb',
            username='user',
            password='pass'
        )
        
        provider = DatabaseProvider(config)
        with provider.connection():
            result = provider.fetch(
                query="SELECT * FROM users WHERE active = %s",
                params=[True]
            )
    """
    
    def __init__(
        self,
        config: DatabaseConfig,
        **kwargs
    ):
        """
        Initialize database provider.
        
        :param config: Database configuration
        """
        super().__init__(**kwargs)
        self._config = config
        self._connection = None
        self._connection_config = {}
        self._validate_database_type()
    
    def _validate_database_type(self):
        """Validate that the required database driver is available."""
        drivers = {
            'sqlite': SQLITE_AVAILABLE,
            'postgres': POSTGRES_AVAILABLE,
            'postgresql': POSTGRES_AVAILABLE,
            'mysql': MYSQL_AVAILABLE,
        }
        
        if self._config.database_type.lower() not in drivers:
            raise ValueError(f"Unsupported database type: {self._config.database_type}")
        
        if not drivers[self._config.database_type.lower()]:
            raise ImportError(
                f"Database driver for {self._config.database_type} is not installed. "
                f"Please install the appropriate package: {self._get_package_name()}"
            )
    
    def _get_package_name(self) -> str:
        """Get the package name to install for the database type."""
        packages = {
            'sqlite': 'No additional package needed (built-in)',
            'postgres': 'psycopg2-binary',
            'postgresql': 'psycopg2-binary',
            'mysql': 'PyMySQL',
        }
        return packages.get(self._config.database_type.lower(), 'Unknown')
    
    def _connect(self) -> None:
        """Establish database connection."""
        db_type = self._config.database_type.lower()
        
        try:
            if db_type == 'sqlite':
                self._connect_sqlite()
            elif db_type in ['postgres', 'postgresql']:
                self._connect_postgres()
            elif db_type == 'mysql':
                self._connect_mysql()
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
                
            # Test connection
            self._test_connection()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}") from e
    
    def _connect_sqlite(self):
        """Connect to SQLite database."""
        if not SQLITE_AVAILABLE:
            raise ImportError("sqlite3 is not available")
        
        database_path = self._config.database or ':memory:'
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row  # Enable dict-like access
    
    def _connect_postgres(self):
        """Connect to PostgreSQL database."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 is not installed")
        
        connection_params = {
            'host': self._config.host,
            'port': self._config.port or 5432,
            'database': self._config.database,
            'user': self._config.username,
            'password': self._config.password,
            'connect_timeout': self._config.connection_timeout,
        }
        
        # Remove None values
        connection_params = {k: v for k, v in connection_params.items() if v is not None}
        
        self._connection = psycopg2.connect(**connection_params)
        self._connection.autocommit = False
    
    def _connect_mysql(self):
        """Connect to MySQL database."""
        if not MYSQL_AVAILABLE:
            raise ImportError("PyMySQL is not installed")
        
        connection_params = {
            'host': self._config.host,
            'port': self._config.port or 3306,
            'database': self._config.database,
            'user': self._config.username,
            'password': self._config.password,
            'connect_timeout': self._config.connection_timeout,
            'charset': 'utf8mb4',
        }
        
        # Remove None values
        connection_params = {k: v for k, v in connection_params.items() if v is not None}
        
        self._connection = pymysql.connect(**connection_params)
    
    def _test_connection(self):
        """Test database connection."""
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}") from e
    
    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            finally:
                self._connection = None
    
    def fetch(
        self,
        query: str,
        params: Optional[Union[List, tuple, Dict]] = None,
        fetch_type: str = "all",
        **kwargs
    ) -> QueryResult[Any]:
        """
        Execute SQL query and fetch data.
        
        :param query: SQL query string
        :param params: Query parameters
        :param fetch_type: 'all', 'one', or 'many'
        :return: QueryResult containing fetched data
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        cursor = self._connection.cursor()
        
        try:
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch data based on type
            if fetch_type == "one":
                row = cursor.fetchone()
                rows = [row] if row else []
            elif fetch_type == "many":
                rows = cursor.fetchmany(size=kwargs.get('size', 10))
            else:  # fetch_type == "all"
                rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            data = []
            for row in rows:
                if isinstance(row, dict):
                    data.append(row)
                elif hasattr(row, 'keys'):  # sqlite3.Row or psycopg2.extras.DictRow
                    data.append(dict(row))
                else:
                    # Handle tuple results (unnamed columns)
                    data.append({'row': row})
            
            # Get total count for SELECT queries
            total_count = len(data)
            metadata = {
                'query': query,
                'params': params,
                'fetch_type': fetch_type,
                'database_type': self._config.database_type,
                'row_count': total_count
            }
            
            # Validate and transform data
            validated_data = []
            for item in data:
                if self.validate(item):
                    transformed_item = self.transform(item)
                    validated_data.append(transformed_item)
                else:
                    self.get_logger().warning(f"Invalid data item: {item}")
            
            return QueryResult(
                data=validated_data,
                total_count=total_count,
                metadata=metadata
            )
            
        except Exception as e:
            self._connection.rollback()
            raise QueryError(f"Database query failed: {e}") from e
        finally:
            cursor.close()
    
    def execute(
        self,
        query: str,
        params: Optional[Union[List, tuple, Dict]] = None,
        commit: bool = True
    ) -> int:
        """
        Execute SQL statement (INSERT, UPDATE, DELETE).
        
        :param query: SQL statement
        :param params: Statement parameters
        :param commit: Whether to commit the transaction
        :return: Number of affected rows
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        cursor = self._connection.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            affected_rows = cursor.rowcount
            
            if commit:
                self._connection.commit()
            
            return affected_rows
            
        except Exception as e:
            self._connection.rollback()
            raise QueryError(f"Database execution failed: {e}") from e
        finally:
            cursor.close()
    
    def execute_many(
        self,
        query: str,
        params_list: List[Union[List, tuple, Dict]],
        commit: bool = True
    ) -> int:
        """
        Execute SQL statement multiple times with different parameters.
        
        :param query: SQL statement
        :param params_list: List of parameter sets
        :param commit: Whether to commit the transaction
        :return: Total number of affected rows
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        cursor = self._connection.cursor()
        
        try:
            cursor.executemany(query, params_list)
            affected_rows = cursor.rowcount
            
            if commit:
                self._connection.commit()
            
            return affected_rows
            
        except Exception as e:
            self._connection.rollback()
            raise QueryError(f"Database execution failed: {e}") from e
        finally:
            cursor.close()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        try:
            yield self
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
    
    def health_check(self) -> bool:
        """Check database health status."""
        try:
            if not self._connection:
                return False
            
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False


#######################################################################
# Async Database Data Provider
#######################################################################
class Database_AsyncDataProvider(AsyncDataProvider[Any]):
    """
    Asynchronous database data provider.
    
    Provides async interface for interacting with SQL databases.
    Currently supports async PostgreSQL (asyncpg) and SQLite (aiosqlite).
    
    Example Usage:
        config = DatabaseConfig(
            database_type='postgres',
            host='localhost',
            database='mydb',
            username='user',
            password='pass'
        )
        
        async def fetch_users():
            provider = AsyncDatabaseProvider(config)
            async with provider.async_connection():
                result = await provider.fetch(
                    query="SELECT * FROM users WHERE active = $1",
                    params=[True]
                )
                return result.data
    """
    
    def __init__(
        self,
        config: DatabaseConfig,
        **kwargs
    ):
        """
        Initialize async database provider.
        
        :param config: Database configuration
        """
        super().__init__(**kwargs)
        self._config = config
        self._connection = None
        self._connection_config = {}
        self._validate_async_database_type()
    
    def _validate_async_database_type(self):
        """Validate that the required async database driver is available."""
        drivers = {
            'sqlite': ASYNC_SQLITE_AVAILABLE,
            'postgres': ASYNC_POSTGRES_AVAILABLE,
            'postgresql': ASYNC_POSTGRES_AVAILABLE,
        }
        
        if self._config.database_type.lower() not in drivers:
            raise ValueError(f"Unsupported async database type: {self._config.database_type}")
        
        if not drivers[self._config.database_type.lower()]:
            raise ImportError(
                f"Async database driver for {self._config.database_type} is not installed. "
                f"Please install the appropriate package: {self._get_async_package_name()}"
            )
    
    def _get_async_package_name(self) -> str:
        """Get the async package name to install for the database type."""
        packages = {
            'sqlite': 'aiosqlite',
            'postgres': 'asyncpg',
            'postgresql': 'asyncpg',
        }
        return packages.get(self._config.database_type.lower(), 'Unknown')
    
    async def _connect(self) -> None:
        """Establish async database connection."""
        db_type = self._config.database_type.lower()
        
        try:
            if db_type == 'sqlite':
                await self._connect_sqlite_async()
            elif db_type in ['postgres', 'postgresql']:
                await self._connect_postgres_async()
            else:
                raise ValueError(f"Unsupported async database type: {db_type}")
                
            # Test connection
            await self._test_async_connection()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}") from e
    
    async def _connect_sqlite_async(self):
        """Connect to SQLite database asynchronously."""
        if not ASYNC_SQLITE_AVAILABLE:
            raise ImportError("aiosqlite is not installed")
        
        database_path = self._config.database or ':memory:'
        self._connection = await aiosqlite.connect(database_path)
        # Enable row factory for dict-like access
        self._connection.row_factory = aiosqlite.Row
    
    async def _connect_postgres_async(self):
        """Connect to PostgreSQL database asynchronously."""
        if not ASYNC_POSTGRES_AVAILABLE:
            raise ImportError("asyncpg is not installed")
        
        dsn_parts = []
        if self._config.username:
            dsn_parts.append(f"user={self._config.username}")
        if self._config.password:
            dsn_parts.append(f"password={self._config.password}")
        if self._config.host:
            dsn_parts.append(f"host={self._config.host}")
        if self._config.port:
            dsn_parts.append(f"port={self._config.port}")
        if self._config.database:
            dsn_parts.append(f"database={self._config.database}")
        
        dsn = " ".join(dsn_parts) if dsn_parts else None
        
        connection_params = {
            'command_timeout': self._config.connection_timeout,
        }
        
        if dsn:
            self._connection = await asyncpg.connect(dsn, **connection_params)
        else:
            # Use environment variables or defaults
            self._connection = await asyncpg.connect(**connection_params)
    
    async def _test_async_connection(self):
        """Test async database connection."""
        try:
            if self._config.database_type.lower() == 'sqlite':
                await self._connection.execute("SELECT 1")
            else:  # PostgreSQL
                await self._connection.fetchval("SELECT 1")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}") from e
    
    async def _disconnect(self) -> None:
        """Close async database connection."""
        if self._connection:
            try:
                await self._connection.close()
            except Exception:
                pass
            finally:
                self._connection = None
    
    async def fetch(
        self,
        query: str,
        params: Optional[Union[List, tuple, Dict]] = None,
        fetch_type: str = "all",
        **kwargs
    ) -> QueryResult[Any]:
        """
        Execute SQL query and fetch data asynchronously.
        
        :param query: SQL query string
        :param params: Query parameters
        :param fetch_type: 'all', 'one', or 'many'
        :return: QueryResult containing fetched data
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        try:
            # Execute query based on database type
            if self._config.database_type.lower() == 'sqlite':
                rows = await self._fetch_sqlite(query, params, fetch_type, **kwargs)
            else:  # PostgreSQL
                rows = await self._fetch_postgres(query, params, fetch_type, **kwargs)
            
            # Convert rows to dictionaries
            data = []
            for row in rows:
                if isinstance(row, dict):
                    data.append(row)
                elif hasattr(row, 'keys'):  # aiosqlite.Row or asyncpg.Record
                    data.append(dict(row))
                else:
                    data.append({'row': row})
            
            # Get total count
            total_count = len(data)
            metadata = {
                'query': query,
                'params': params,
                'fetch_type': fetch_type,
                'database_type': self._config.database_type,
                'row_count': total_count
            }
            
            # Validate and transform data
            validated_data = []
            for item in data:
                if await self.validate(item):
                    transformed_item = await self.transform(item)
                    validated_data.append(transformed_item)
                else:
                    self.get_logger().warning(f"Invalid data item: {item}")
            
            return QueryResult(
                data=validated_data,
                total_count=total_count,
                metadata=metadata
            )
            
        except Exception as e:
            raise QueryError(f"Database query failed: {e}") from e
    
    async def _fetch_sqlite(self, query: str, params, fetch_type: str, **kwargs):
        """Fetch data from SQLite asynchronously."""
        cursor = await self._connection.execute(query, params or ())
        
        if fetch_type == "one":
            row = await cursor.fetchone()
            rows = [row] if row else []
        elif fetch_type == "many":
            rows = await cursor.fetchmany(size=kwargs.get('size', 10))
        else:  # fetch_type == "all"
            rows = await cursor.fetchall()
        
        await cursor.close()
        return rows
    
    async def _fetch_postgres(self, query: str, params, fetch_type: str, **kwargs):
        """Fetch data from PostgreSQL asynchronously."""
        if fetch_type == "one":
            row = await self._connection.fetchrow(query, *params) if params else await self._connection.fetchrow(query)
            rows = [row] if row else []
        elif fetch_type == "many":
            rows = await self._connection.fetch(query, *params) if params else await self._connection.fetch(query)
            rows = rows[:kwargs.get('size', 10)]
        else:  # fetch_type == "all"
            rows = await self._connection.fetch(query, *params) if params else await self._connection.fetch(query)
        
        return rows
    
    async def execute(
        self,
        query: str,
        params: Optional[Union[List, tuple, Dict]] = None,
        commit: bool = True
    ) -> int:
        """
        Execute SQL statement asynchronously.
        
        :param query: SQL statement
        :param params: Statement parameters
        :param commit: Whether to commit the transaction
        :return: Number of affected rows
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        try:
            if self._config.database_type.lower() == 'sqlite':
                cursor = await self._connection.execute(query, params or ())
                affected_rows = cursor.rowcount
                await cursor.close()
            else:  # PostgreSQL
                if params:
                    affected_rows = await self._connection.execute(query, *params)
                else:
                    affected_rows = await self._connection.execute(query)
                affected_rows = affected_rows.split()[-1] if isinstance(affected_rows, str) else 0
            
            return affected_rows
            
        except Exception as e:
            raise QueryError(f"Database execution failed: {e}") from e
    
    async def execute_many(
        self,
        query: str,
        params_list: List[Union[List, tuple, Dict]],
        commit: bool = True
    ) -> int:
        """
        Execute SQL statement multiple times asynchronously.
        
        :param query: SQL statement
        :param params_list: List of parameter sets
        :param commit: Whether to commit the transaction
        :return: Total number of affected rows
        """
        if not self._connection:
            raise ConnectionError("Not connected to database")
        
        try:
            if self._config.database_type.lower() == 'sqlite':
                await self._connection.executemany(query, params_list)
                affected_rows = len(params_list)  # SQLite doesn't return rowcount for executemany
            else:  # PostgreSQL
                # asyncpg doesn't have executemany, so we'll use transactions
                async with self._connection.transaction():
                    for params in params_list:
                        if params:
                            await self._connection.execute(query, *params)
                        else:
                            await self._connection.execute(query)
                    affected_rows = len(params_list)
            
            return affected_rows
            
        except Exception as e:
            raise QueryError(f"Database execution failed: {e}") from e
    
    async def health_check(self) -> bool:
        """Check async database health status."""
        try:
            if not self._connection:
                return False
            
            if self._config.database_type.lower() == 'sqlite':
                await self._connection.execute("SELECT 1")
            else:  # PostgreSQL
                await self._connection.fetchval("SELECT 1")
            return True
        except Exception:
            return False
