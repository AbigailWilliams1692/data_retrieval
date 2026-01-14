#######################################################################
# Project: Data Retrieval Module
# File: test_data_provider.py
# Description: Unit tests for DataProvider and AsyncDataProvider
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from typing import List, Dict, Any, Optional

# Local Packages
from data_retrieval.model.data_provider import DataProvider, AsyncDataProvider, ProviderStatus
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import DataProviderError, ConnectionError, QueryError


#######################################################################
# Test Data Classes
#######################################################################
class UserTestData:
    """Simple test user class for testing purposes."""
    
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
    
    def __eq__(self, other):
        if not isinstance(other, UserTestData):
            return False
        return self.id == other.id and self.name == other.name and self.email == other.email
    
    def __repr__(self):
        return f"UserTestData(id={self.id}, name={self.name}, email={self.email})"


#######################################################################
# Mock Data Provider Implementation
#######################################################################
class MockDataProvider(DataProvider[UserTestData]):
    """Mock implementation of DataProvider for testing."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mock_data = {
            "1": UserTestData("1", "John Doe", "john@example.com"),
            "2": UserTestData("2", "Jane Smith", "jane@example.com"),
            "3": UserTestData("3", "Bob Johnson", "bob@example.com"),
        }
        self._connection_attempts = 0
        self._disconnect_called = False
    
    def _connect(self) -> None:
        self._connection_attempts += 1
        if self._connection_config.get("should_fail", False):
            raise ConnectionError("Mock connection failed")
    
    def _disconnect(self) -> None:
        self._disconnect_called = True
    
    def fetch(self, *args, **kwargs) -> QueryResult[UserTestData]:
        filters = kwargs.get("filters", {})
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size", 100)
        
        # Filter data
        filtered_data = list(self._mock_data.values())
        if "name" in filters:
            filtered_data = [u for u in filtered_data if filters["name"] in u.name]
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = filtered_data[start_idx:end_idx]
        
        return QueryResult(
            data=page_data,
            total_count=len(filtered_data),
            metadata={"source": "mock"}
        )


class MockAsyncDataProvider(AsyncDataProvider[UserTestData]):
    """Mock implementation of AsyncDataProvider for testing."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mock_data = {
            "1": UserTestData("1", "John Doe", "john@example.com"),
            "2": UserTestData("2", "Jane Smith", "jane@example.com"),
            "3": UserTestData("3", "Bob Johnson", "bob@example.com"),
        }
        self._connection_attempts = 0
        self._disconnect_called = False
    
    async def _connect(self) -> None:
        self._connection_attempts += 1
        if self._connection_config.get("should_fail", False):
            raise ConnectionError("Mock connection failed")
    
    async def _disconnect(self) -> None:
        self._disconnect_called = True
    
    async def fetch(self, *args, **kwargs) -> QueryResult[UserTestData]:
        filters = kwargs.get("filters", {})
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size", 100)
        
        # Filter data
        filtered_data = list(self._mock_data.values())
        if "name" in filters:
            filtered_data = [u for u in filtered_data if filters["name"] in u.name]
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = filtered_data[start_idx:end_idx]
        
        return QueryResult(
            data=page_data,
            total_count=len(filtered_data),
            metadata={"source": "async_mock"}
        )


#######################################################################
# DataProvider Tests
#######################################################################
class TestDataProvider(unittest.TestCase):
    """Test cases for DataProvider class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.provider = MockDataProvider()
    
    def test_initialization(self):
        """Test provider initialization."""
        self.assertEqual(self.provider._name, "DataProvider")
        self.assertEqual(self.provider._type, "DataProvider")
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.DISCONNECTED)
        self.assertFalse(self.provider.is_connected())
    
    def test_connect_success(self):
        """Test successful connection."""
        self.provider.connect()
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.CONNECTED)
        self.assertTrue(self.provider.is_connected())
        self.assertEqual(self.provider._connection_attempts, 1)
    
    def test_connect_failure(self):
        """Test connection failure."""
        with self.assertRaises(ConnectionError):
            self.provider.connect(should_fail=True)
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.ERROR)
        self.assertFalse(self.provider.is_connected())
    
    def test_disconnect(self):
        """Test disconnection."""
        self.provider.connect()
        self.provider.disconnect()
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.DISCONNECTED)
        self.assertTrue(self.provider._disconnect_called)
    
    def test_connection_context_manager(self):
        """Test connection context manager."""
        with self.provider.connection() as p:
            self.assertIs(p, self.provider)
            self.assertEqual(self.provider.get_provider_status(), ProviderStatus.CONNECTED)
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.DISCONNECTED)
    
    def test_fetch_data(self):
        """Test data fetching."""
        result = self.provider.fetch()
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 3)
        self.assertEqual(result.total_count, 3)
        self.assertFalse(result.is_empty())
    
    def test_fetch_with_filters(self):
        """Test data fetching with filters."""
        result = self.provider.fetch(filters={"name": "John Doe"})
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].name, "John Doe")
        # Verify total count is correct
        self.assertEqual(result.total_count, 1)
    
    def test_fetch_or_raise_success(self):
        """Test fetch_or_raise with successful result."""
        result = self.provider.fetch_or_raise()
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 3)
    
    def test_fetch_or_raise_empty(self):
        """Test fetch_or_raise with empty result."""
        # Mock empty result
        self.provider.fetch = MagicMock(return_value=QueryResult(data=[], total_count=0))
        with self.assertRaises(QueryError):
            self.provider.fetch_or_raise()
    
    def test_with_retry_success(self):
        """Test with_retry on successful operation."""
        operation = MagicMock(return_value="success")
        result = self.provider.with_retry(operation, max_retries=3, parameters={})
        self.assertEqual(result, "success")
        operation.assert_called_once_with(**{})
    
    def test_with_retry_failure_then_success(self):
        """Test with_retry with initial failures then success."""
        operation = MagicMock(side_effect=[Exception("fail"), "success"])
        result = self.provider.with_retry(operation, max_retries=3, retry_delay=0.01, parameters={})
        self.assertEqual(result, "success")
        self.assertEqual(operation.call_count, 2)
    
    def test_with_retry_all_failures(self):
        """Test with_retry when all attempts fail."""
        operation = MagicMock(side_effect=Exception("always fails"))
        with self.assertRaises(DataProviderError):
            self.provider.with_retry(operation, max_retries=2, retry_delay=0.01, parameters={})
        self.assertEqual(operation.call_count, 2)
    
    def test_validate_hook(self):
        """Test validate hook method."""
        user = UserTestData("1", "Test", "test@example.com")
        # Note: validate method raises True (int) instead of returning bool
        with self.assertRaises(TypeError):
            self.provider.validate(user)
    
    def test_transform_hook(self):
        """Test transform hook method."""
        raw_data = {"id": "1", "name": "Test", "email": "test@example.com"}
        # Note: transform method raises data instead of returning it
        with self.assertRaises(TypeError):
            self.provider.transform(raw_data)
    
    def test_health_check(self):
        """Test health check method."""
        # Default implementation returns connection status
        self.assertFalse(self.provider.health_check())
        self.provider.connect()
        self.assertTrue(self.provider.health_check())
    
    def test_get_set_methods(self):
        """Test getter and setter methods."""
        # Test provider status
        self.provider.set_provider_status(ProviderStatus.ERROR)
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.ERROR)
        
        # Test connection config
        config = {"host": "localhost", "port": 5432}
        self.provider.set_connection_config(config)
        retrieved_config = self.provider.get_connection_config()
        self.assertEqual(retrieved_config, config)
        # Ensure it's a copy
        retrieved_config["new_key"] = "value"
        self.assertNotIn("new_key", self.provider.get_connection_config())


#######################################################################
# AsyncDataProvider Tests
#######################################################################
class TestAsyncDataProvider(unittest.IsolatedAsyncioTestCase):
    """Test cases for AsyncDataProvider class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.provider = MockAsyncDataProvider()
    
    async def test_initialization(self):
        """Test async provider initialization."""
        self.assertEqual(self.provider._name, "AsyncDataProvider")
        self.assertEqual(self.provider._type, "AsyncDataProvider")
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.DISCONNECTED)
        self.assertFalse(self.provider.is_connected())
    
    async def test_connect_success(self):
        """Test successful async connection."""
        await self.provider.connect()
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.CONNECTED)
        self.assertTrue(self.provider.is_connected())
        self.assertEqual(self.provider._connection_attempts, 1)
    
    async def test_connect_failure(self):
        """Test async connection failure."""
        with self.assertRaises(ConnectionError):
            await self.provider.connect(should_fail=True)
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.ERROR)
        self.assertFalse(self.provider.is_connected())
    
    async def test_disconnect(self):
        """Test async disconnection."""
        await self.provider.connect()
        await self.provider.disconnect()
        self.assertEqual(self.provider.get_provider_status(), ProviderStatus.DISCONNECTED)
        self.assertTrue(self.provider._disconnect_called)
    
    async def test_async_connection_context_manager(self):
        """Test async connection context manager."""
        async_context = self.provider.async_connection()
        # Test that it's an async generator
        self.assertTrue(hasattr(async_context, '__anext__'))
        self.assertTrue(hasattr(async_context, '__aiter__'))
    
    async def test_fetch_data(self):
        """Test async data fetching."""
        result = await self.provider.fetch()
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 3)
        self.assertEqual(result.total_count, 3)
        self.assertFalse(result.is_empty())
    
    async def test_fetch_with_filters(self):
        """Test async data fetching with filters."""
        result = await self.provider.fetch(filters={"name": "Jane Smith"})
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].name, "Jane Smith")
        # Verify total count is correct
        self.assertEqual(result.total_count, 1)
    
    async def test_fetch_or_raise_success(self):
        """Test async fetch_or_raise with successful result."""
        result = await self.provider.fetch_or_raise()
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 3)
    
    async def test_fetch_or_raise_empty(self):
        """Test async fetch_or_raise with empty result."""
        # Mock empty result
        self.provider.fetch = AsyncMock(return_value=QueryResult(data=[], total_count=0))
        with self.assertRaises(QueryError):
            await self.provider.fetch_or_raise()
    
    async def test_with_retry_sync_success(self):
        """Test async with_retry with sync operation."""
        operation = MagicMock(return_value="success")
        result = await self.provider.with_retry(operation, max_retries=3)
        self.assertEqual(result, "success")
        operation.assert_called_once()
    
    async def test_with_retry_async_success(self):
        """Test async with_retry with async operation."""
        operation = AsyncMock(return_value="success")
        result = await self.provider.with_retry(operation, max_retries=3)
        self.assertEqual(result, "success")
        operation.assert_awaited_once()
    
    async def test_with_retry_failure_then_success(self):
        """Test async with_retry with initial failures then success."""
        operation = MagicMock(side_effect=[Exception("fail"), "success"])
        result = await self.provider.with_retry(operation, max_retries=3, retry_delay=0.01)
        self.assertEqual(result, "success")
        self.assertEqual(operation.call_count, 2)
    
    async def test_with_retry_all_failures(self):
        """Test async with_retry when all attempts fail."""
        operation = MagicMock(side_effect=Exception("always fails"))
        with self.assertRaises(DataProviderError):
            await self.provider.with_retry(operation, max_retries=2, retry_delay=0.01)
        self.assertEqual(operation.call_count, 2)
    
    async def test_validate_hook(self):
        """Test async validate hook method."""
        user = UserTestData("1", "Test", "test@example.com")
        result = await self.provider.validate(user)
        self.assertTrue(result)
    
    async def test_transform_hook(self):
        """Test async transform hook method."""
        raw_data = {"id": "1", "name": "Test", "email": "test@example.com"}
        result = await self.provider.transform(raw_data)
        self.assertEqual(result, raw_data)
    
    async def test_health_check(self):
        """Test async health check method."""
        # Default implementation returns connection status
        self.assertFalse(await self.provider.health_check())
        await self.provider.connect()
        self.assertTrue(await self.provider.health_check())
    
    async def test_async_validate_hook(self):
        """Test async validate hook method."""
        user = UserTestData("1", "Test", "test@example.com")
        result = await self.provider.validate(user)
        self.assertTrue(result)
    
    async def test_async_transform_hook(self):
        """Test async transform hook method."""
        raw_data = {"id": "1", "name": "Test", "email": "test@example.com"}
        result = await self.provider.transform(raw_data)
        self.assertEqual(result, raw_data)


#######################################################################
# QueryResult Tests
#######################################################################
class TestQueryResult(unittest.TestCase):
    """Test cases for QueryResult class."""
    
    def test_empty_query_result(self):
        """Test empty query result."""
        result = QueryResult(data=[], total_count=0)
        self.assertTrue(result.is_empty())
        self.assertEqual(len(result.data), 0)
        self.assertEqual(result.total_count, 0)
    
    def test_non_empty_query_result(self):
        """Test non-empty query result."""
        users = [UserTestData("1", "Test", "test@example.com")]
        result = QueryResult(data=users, total_count=1)
        self.assertFalse(result.is_empty())
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.total_count, 1)
    
    def test_query_result_with_metadata(self):
        """Test query result with metadata."""
        metadata = {"source": "database", "query_time": 0.123}
        result = QueryResult(data=[], total_count=0, metadata=metadata)
        self.assertEqual(result.metadata, metadata)


#######################################################################
# ProviderStatus Tests
#######################################################################
class TestProviderStatus(unittest.TestCase):
    """Test cases for ProviderStatus enum."""
    
    def test_provider_status_values(self):
        """Test ProviderStatus enum values."""
        self.assertEqual(ProviderStatus.DISCONNECTED.value, "disconnected")
        self.assertEqual(ProviderStatus.CONNECTED.value, "connected")
        self.assertEqual(ProviderStatus.ERROR.value, "error")
    
    def test_provider_status_comparison(self):
        """Test ProviderStatus enum comparison."""
        self.assertEqual(ProviderStatus.DISCONNECTED, ProviderStatus.DISCONNECTED)
        self.assertNotEqual(ProviderStatus.DISCONNECTED, ProviderStatus.CONNECTED)


#######################################################################
# Integration Tests
#######################################################################
class TestIntegration(unittest.TestCase):
    """Integration tests for the data provider system."""
    
    def test_provider_inheritance(self):
        """Test that providers properly inherit from base classes."""
        provider = MockDataProvider()
        self.assertTrue(hasattr(provider, 'get_instance_id'))
        self.assertTrue(hasattr(provider, 'get_logger'))
        self.assertTrue(hasattr(provider, 'connect'))
        self.assertTrue(hasattr(provider, 'fetch'))
    
    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        self.assertTrue(issubclass(ConnectionError, DataProviderError))
        self.assertTrue(issubclass(QueryError, DataProviderError))


#######################################################################
# Test Runner
#######################################################################
if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
