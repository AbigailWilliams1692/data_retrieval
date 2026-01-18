#!/usr/bin/env python3
"""
Unit tests for Database data providers.

Author: AbigailWilliams1692
Created: 2026-01-14
"""

import asyncio
import sqlite3
import os
from unittest.mock import MagicMock, patch, AsyncMock
import unittest

from data_retrieval.data_provider.database import Database_DataProvider, Database_AsyncDataProvider, DatabaseConfig
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import DataProviderConnectionError, DataFetchError


class TestDatabaseConfig(unittest.TestCase):
    """Test cases for DatabaseConfig."""
    
    def test_database_config_creation(self):
        """Test creating database configuration."""
        config = DatabaseConfig(
            database_type='sqlite',
            database='test.db'
        )
        
        self.assertEqual(config.database_type, 'sqlite')
        self.assertEqual(config.database, 'test.db')
        self.assertIsNone(config.host)
        self.assertIsNone(config.username)
    
    def test_postgres_config(self):
        """Test PostgreSQL configuration."""
        config = DatabaseConfig(
            database_type='postgres',
            host='localhost',
            port=5432,
            database='mydb',
            username='user',
            password='pass'
        )
        
        self.assertEqual(config.database_type, 'postgres')
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.database, 'mydb')
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.password, 'pass')


class Test_Database_DataProvider(unittest.TestCase):
    """Test cases for DatabaseProvider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = DatabaseConfig(
            database_type='sqlite',
            database=':memory:'
        )
        self.provider = Database_DataProvider(self.config)
        
        # Create a test database
        self.test_db_path = 'test.db'
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_initialization(self):
        """Test provider initialization."""
        self.assertEqual(self.provider._config.database_type, 'sqlite')
        self.assertEqual(self.provider._config.database, ':memory:')
        self.assertIsNone(self.provider._connection)
    
    def test_validate_database_type_sqlite(self):
        """Test validating SQLite database type."""
        # Should not raise exception
        self.provider._validate_database_type()
    
    def test_validate_database_type_unsupported(self):
        """Test validating unsupported database type."""
        config = DatabaseConfig(database_type='unsupported')
        provider = Database_DataProvider(config)
        
        with self.assertRaises(ValueError):
            provider._validate_database_type()
    
    def test_connect_sqlite(self):
        """Test connecting to SQLite database."""
        config = DatabaseConfig(database_type='sqlite', database=self.test_db_path)
        provider = Database_DataProvider(config)
        
        provider._connect()
        
        self.assertIsNotNone(provider._connection)
        self.assertIsInstance(provider._connection, sqlite3.Connection)
        
        provider._disconnect()
    
    def test_connect_sqlite_failure(self):
        """Test SQLite connection failure."""
        config = DatabaseConfig(database_type='sqlite', database='/invalid/path/test.db')
        provider = Database_DataProvider(config)
        
        with self.assertRaises(DataProviderConnectionError):
            provider._connect()
    
    @patch('psycopg2.connect')
    def test_connect_postgres(self, mock_connect):
        """Test connecting to PostgreSQL database."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig(
            database_type='postgres',
            host='localhost',
            database='testdb',
            username='user',
            password='pass'
        )
        provider = Database_DataProvider(config)
        
        provider._connect()
        
        mock_connect.assert_called_once()
        self.assertIsNotNone(provider._connection)
        
        provider._disconnect()
    
    def test_disconnect(self):
        """Test disconnection."""
        mock_connection = MagicMock()
        self.provider._connection = mock_connection
        
        self.provider._disconnect()
        
        mock_connection.close.assert_called_once()
        self.assertIsNone(self.provider._connection)
    
    def test_fetch_all_records(self):
        """Test fetching all records."""
        # Set up in-memory database with test data
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        # Create test table and data
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
        ''')
        cursor.execute('''
            INSERT INTO users (name, email) VALUES (?, ?), (?, ?)
        ''', ('Alice', 'alice@example.com', 'Bob', 'bob@example.com'))
        provider._connection.commit()
        cursor.close()
        
        # Fetch data
        result = provider.fetch("SELECT * FROM users")
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(result.data[0]['name'], 'Alice')
        self.assertEqual(result.data[1]['name'], 'Bob')
        
        provider._disconnect()
    
    def test_fetch_with_params(self):
        """Test fetching with parameters."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        # Set up test data
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)
        ''')
        cursor.execute('''
            INSERT INTO users (name, age) VALUES (?, ?), (?, ?), (?, ?)
        ''', ('Alice', 25, 'Bob', 30, 'Charlie', 35))
        provider._connection.commit()
        cursor.close()
        
        # Fetch with parameters
        result = provider.fetch(
            "SELECT * FROM users WHERE age > ?",
            params=[28]
        )
        
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]['name'], 'Bob')
        self.assertEqual(result.data[1]['name'], 'Charlie')
        
        provider._disconnect()
    
    def test_fetch_one_record(self):
        """Test fetching one record."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        # Set up test data
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        cursor.execute('INSERT INTO users (name) VALUES (?)', ('Alice',))
        provider._connection.commit()
        cursor.close()
        
        # Fetch one record
        result = provider.fetch("SELECT * FROM users", fetch_type="one")
        
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]['name'], 'Alice')
        
        provider._disconnect()
    
    def test_execute_insert(self):
        """Test executing INSERT statement."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        provider._connection.commit()
        cursor.close()
        
        # Execute INSERT
        affected_rows = provider.execute(
            "INSERT INTO users (name) VALUES (?)",
            params=['Alice']
        )
        
        self.assertEqual(affected_rows, 1)
        
        # Verify insertion
        result = provider.fetch("SELECT * FROM users")
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]['name'], 'Alice')
        
        provider._disconnect()
    
    def test_execute_update(self):
        """Test executing UPDATE statement."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        cursor.execute('INSERT INTO users (name) VALUES (?)', ('Alice',))
        provider._connection.commit()
        cursor.close()
        
        # Execute UPDATE
        affected_rows = provider.execute(
            "UPDATE users SET name = ? WHERE name = ?",
            params=['Bob', 'Alice']
        )
        
        self.assertEqual(affected_rows, 1)
        
        # Verify update
        result = provider.fetch("SELECT * FROM users")
        self.assertEqual(result.data[0]['name'], 'Bob')
        
        provider._disconnect()
    
    def test_execute_many(self):
        """Test executing multiple statements."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        provider._connection.commit()
        cursor.close()
        
        # Execute multiple INSERTs
        users_data = [
            ('Alice',),
            ('Bob',),
            ('Charlie',)
        ]
        affected_rows = provider.execute_many(
            "INSERT INTO users (name) VALUES (?)",
            params_list=users_data
        )
        
        self.assertEqual(affected_rows, 3)
        
        # Verify insertions
        result = provider.fetch("SELECT * FROM users")
        self.assertEqual(len(result.data), 3)
        
        provider._disconnect()
    
    def test_transaction_success(self):
        """Test successful transaction."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        provider._connection.commit()
        cursor.close()
        
        # Use transaction
        with provider.transaction():
            provider.execute("INSERT INTO users (name) VALUES (?)", params=['Alice'], commit=False)
            provider.execute("INSERT INTO users (name) VALUES (?)", params=['Bob'], commit=False)
        
        # Verify both inserts were committed
        result = provider.fetch("SELECT * FROM users")
        self.assertEqual(len(result.data), 2)
        
        provider._disconnect()
    
    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        cursor = provider._connection.cursor()
        cursor.execute('''
            CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
        ''')
        provider._connection.commit()
        cursor.close()
        
        # Insert one record first
        provider.execute("INSERT INTO users (name) VALUES (?)", params=['Alice'])
        
        # Try transaction that fails
        try:
            with provider.transaction():
                provider.execute("INSERT INTO users (name) VALUES (?)", params=['Bob'], commit=False)
                # This will cause an error
                provider.execute("INSERT INTO nonexistent_table VALUES (?)", params=['Charlie'], commit=False)
        except DataFetchError:
            pass  # Expected error
        
        # Verify only first insert was committed
        result = provider.fetch("SELECT * FROM users")
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]['name'], 'Alice')
        
        provider._disconnect()
    
    def test_health_check_success(self):
        """Test successful health check."""
        config = DatabaseConfig(database_type='sqlite', database=':memory:')
        provider = Database_DataProvider(config)
        
        provider._connect()
        
        result = provider.health_check()
        
        self.assertTrue(result)
        
        provider._disconnect()
    
    def test_health_check_failure(self):
        """Test health check failure."""
        result = self.provider.health_check()
        
        self.assertFalse(result)
    
    def test_fetch_without_connection(self):
        """Test fetching without connection."""
        with self.assertRaises(DataProviderConnectionError):
            self.provider.fetch("SELECT 1")
    
    def test_execute_without_connection(self):
        """Test executing without connection."""
        with self.assertRaises(DataProviderConnectionError):
            self.provider.execute("SELECT 1")


class Test_Database_AsyncDataProvider(unittest.IsolatedAsyncioTestCase):
    """Test cases for Database_AsyncDataProvider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = DatabaseConfig(
            database_type='sqlite',
            database=':memory:'
        )
        self.provider = Database_AsyncDataProvider(self.config)
    
    def test_initialization(self):
        """Test async provider initialization."""
        self.assertEqual(self.provider._config.database_type, 'sqlite')
        self.assertIsNone(self.provider._connection)
    
    def test_validate_async_database_type_sqlite(self):
        """Test validating SQLite database type for async."""
        self.provider._validate_async_database_type()
    
    def test_validate_async_database_type_unsupported(self):
        """Test validating unsupported async database type."""
        config = DatabaseConfig(database_type='unsupported')
        provider = Database_AsyncDataProvider(config)
        
        with self.assertRaises(ValueError):
            provider._validate_async_database_type()
    
    @patch('aiosqlite.connect')
    async def test_connect_sqlite_async(self, mock_connect):
        """Test connecting to SQLite database asynchronously."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection
        mock_connection.execute.return_value.__aenter__.return_value = AsyncMock()
        
        await self.provider._connect()
        
        mock_connect.assert_called_once_with(':memory:')
        self.assertIsNotNone(self.provider._connection)
        
        await self.provider._disconnect()
    
    @patch('asyncpg.connect')
    async def test_connect_postgres_async(self, mock_connect):
        """Test connecting to PostgreSQL database asynchronously."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection
        mock_connection.fetchval.return_value = 1
        
        config = DatabaseConfig(
            database_type='postgres',
            host='localhost',
            database='testdb',
            username='user',
            password='pass'
        )
        provider = Database_AsyncDataProvider(config)
        
        await provider._connect()
        
        mock_connect.assert_called_once()
        self.assertIsNotNone(provider._connection)
        
        await provider._disconnect()
    
    async def test_disconnect_async(self):
        """Test async disconnection."""
        mock_connection = AsyncMock()
        self.provider._connection = mock_connection
        
        await self.provider._disconnect()
        
        mock_connection.close.assert_called_once()
        self.assertIsNone(self.provider._connection)
    
    @patch('aiosqlite.connect')
    async def test_fetch_sqlite_async(self, mock_connect):
        """Test fetching from SQLite asynchronously."""
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_connection.execute.return_value.__aenter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        mock_connect.return_value = mock_connection
        
        await self.provider._connect()
        
        result = await self.provider.fetch("SELECT * FROM users")
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]['name'], 'Alice')
        
        await self.provider._disconnect()
    
    @patch('asyncpg.connect')
    async def test_fetch_postgres_async(self, mock_connect):
        """Test fetching from PostgreSQL asynchronously."""
        mock_connection = AsyncMock()
        mock_connection.fetch.return_value = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig(database_type='postgres')
        provider = Database_AsyncDataProvider(config)
        await provider._connect()
        
        result = await provider.provider.fetch("SELECT * FROM users")
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 2)
        
        await provider._disconnect()
    
    @patch('aiosqlite.connect')
    async def test_execute_sqlite_async(self, mock_connect):
        """Test executing SQLite statement asynchronously."""
        mock_connection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.rowcount = 1
        mock_connection.execute.return_value.__aenter__.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        await self.provider._connect()
        
        affected_rows = await self.provider.execute(
            "INSERT INTO users (name) VALUES (?)",
            params=['Alice']
        )
        
        self.assertEqual(affected_rows, 1)
        
        await self.provider._disconnect()
    
    @patch('asyncpg.connect')
    async def test_execute_postgres_async(self, mock_connect):
        """Test executing PostgreSQL statement asynchronously."""
        mock_connection = AsyncMock()
        mock_connection.execute.return_value = "INSERT 0 1"
        mock_connect.return_value = mock_connection
        
        config = DatabaseConfig(database_type='postgres')
        provider = Database_AsyncDataProvider(config)
        await provider._connect()
        
        affected_rows = await self.provider.execute(
            "INSERT INTO users (name) VALUES ($1)",
            params=['Alice']
        )
        
        # PostgreSQL returns string like "INSERT 0 1"
        self.assertEqual(affected_rows, 1)
        
        await provider._disconnect()
    
    @patch('aiosqlite.connect')
    async def test_health_check_success_async(self, mock_connect):
        """Test successful async health check."""
        mock_connection = AsyncMock()
        mock_connection.execute.return_value.__aenter__.return_value = AsyncMock()
        mock_connect.return_value = mock_connection
        
        await self.provider._connect()
        
        result = await self.provider.health_check()
        
        self.assertTrue(result)
        
        await self.provider._disconnect()
    
    async def test_health_check_failure_async(self):
        """Test async health check failure."""
        result = await self.provider.health_check()
        
        self.assertFalse(result)
    
    async def test_fetch_without_connection_async(self):
        """Test fetching without async connection."""
        with self.assertRaises(DataProviderConnectionError):
            await self.provider.fetch("SELECT 1")


if __name__ == '__main__':
    unittest.main()
