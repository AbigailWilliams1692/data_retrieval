#######################################################################
# Project: Data Retrieval Module
# File: conftest.py
# Description: Pytest configuration and fixtures
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from typing import Generator, AsyncGenerator

# Local Packages
from data_retrieval.model.data_provider import DataProvider, AsyncDataProvider, DataProviderConnectionStatus
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import DataProviderError, DataProviderConnectionError, DataFetchError

#######################################################################
# Test Fixtures
#######################################################################
@pytest.fixture
def sample_data():
    """Fixture providing sample test data."""
    return [
        {"id": "1", "name": "John Doe", "email": "john@example.com"},
        {"id": "2", "name": "Jane Smith", "email": "jane@example.com"},
        {"id": "3", "name": "Bob Johnson", "email": "bob@example.com"},
    ]

@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger

@pytest.fixture
def sync_data_provider(mock_logger):
    """Fixture providing a synchronous data provider for testing."""
    class TestDataProvider(DataProvider):
        def __init__(self, logger=None):
            super().__init__(logger=logger)
            self._connected = False
            self._data = [
                {"id": "1", "name": "John Doe"},
                {"id": "2", "name": "Jane Smith"},
            ]
        
        def _connect(self) -> None:
            self._connected = True
        
        def _disconnect(self) -> None:
            self._connected = False
        
        def fetch(self, *args, **kwargs) -> QueryResult:
            filters = kwargs.get("filters", {})
            data = self._data
            
            if "name" in filters:
                data = [item for item in data if filters["name"] in item["name"]]
            
            return QueryResult(data=data, total_count=len(data))
    
    return TestDataProvider(logger=mock_logger)

@pytest.fixture
async def async_data_provider(mock_logger):
    """Fixture providing an asynchronous data provider for testing."""
    class TestAsyncDataProvider(AsyncDataProvider):
        def __init__(self, logger=None):
            super().__init__(logger=logger)
            self._connected = False
            self._data = [
                {"id": "1", "name": "John Doe"},
                {"id": "2", "name": "Jane Smith"},
            ]
        
        async def _connect(self) -> None:
            self._connected = True
        
        async def _disconnect(self) -> None:
            self._connected = False
        
        async def fetch(self, *args, **kwargs) -> QueryResult:
            filters = kwargs.get("filters", {})
            data = self._data
            
            if "name" in filters:
                data = [item for item in data if filters["name"] in item["name"]]
            
            return QueryResult(data=data, total_count=len(data))
    
    return TestAsyncDataProvider(logger=mock_logger)

@pytest.fixture
def mock_query_result():
    """Fixture providing a mock query result."""
    return QueryResult(
        data=[{"id": "1", "name": "Test"}],
        total_count=1,
        metadata={"source": "test"}
    )

@pytest.fixture
def event_loop():
    """Fixture providing an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

#######################################################################
# Test Markers
#######################################################################
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "async_test: mark test as async test"
    )

#######################################################################
# Helper Functions
#######################################################################
def create_mock_provider_with_failure(fail_connect=False, fail_fetch=False):
    """Create a mock provider that can be configured to fail."""
    class FailingDataProvider(DataProvider):
        def __init__(self, fail_connect=False, fail_fetch=False):
            super().__init__()
            self.fail_connect = fail_connect
            self.fail_fetch = fail_fetch
            self._connected = False
        
        def _connect(self) -> None:
            if self.fail_connect:
                raise DataProviderConnectionError("Connection failed")
            self._connected = True
        
        def _disconnect(self) -> None:
            self._connected = False
        
        def fetch(self, *args, **kwargs) -> QueryResult:
            if self.fail_fetch:
                raise DataFetchError("Fetch failed")
            return QueryResult(data=[], total_count=0)
    
    return FailingDataProvider(fail_connect, fail_fetch)

async def create_async_mock_provider_with_failure(fail_connect=False, fail_fetch=False):
    """Create an async mock provider that can be configured to fail."""
    class FailingAsyncDataProvider(AsyncDataProvider):
        def __init__(self, fail_connect=False, fail_fetch=False):
            super().__init__()
            self.fail_connect = fail_connect
            self.fail_fetch = fail_fetch
            self._connected = False
        
        async def _connect(self) -> None:
            if self.fail_connect:
                raise DataProviderConnectionError("Connection failed")
            self._connected = True
        
        async def _disconnect(self) -> None:
            self._connected = False
        
        async def fetch(self, *args, **kwargs) -> QueryResult:
            if self.fail_fetch:
                raise DataFetchError("Fetch failed")
            return QueryResult(data=[], total_count=0)
    
    return FailingAsyncDataProvider(fail_connect, fail_fetch)
