#######################################################################
# Project: Data Retrieval Module
# File: data_provider.py
# Description: Abstract base class for data providers
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2025-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import (
    Any,
    Generic,
    TypeVar,
    Optional,
    Dict,
    List,
    Iterator,
    Callable,
)

# Local Packages
from data_retrieval.model.data_module import DataModule
from data_retrieval.model.exceptions import (
    DataProviderError,
    ConnectionError,
    QueryError,
)
from data_retrieval.model.query_result import QueryResult



#######################################################################
# Constants
#######################################################################
T = TypeVar("T")


#######################################################################
# Enums & Data Classes
#######################################################################
class ProviderStatus(Enum):
    """
    Enumeration of provider connection states.
    """

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


#######################################################################
# Data Provider Class
#######################################################################
class DataProvider(ABC, DataModule, Generic[T]):
    """
    Abstract base class for data providers with standardized synchronous API interface.

    This class provides a unified interface for retrieving data from various sources
    (APIs, databases, files, etc.). Subclasses must implement the abstract methods
    to provide source-specific data retrieval logic.

    Type Parameters:
        T: The type of data entity this provider handles.

    Example Usage:
        class UserProvider(DataProvider[User]):
            def _connect(self) -> None:
                self._db = Database.connect(...)

            def get_by_id(self, identifier: str) -> Optional[User]:
                return self._db.users.find_one(id=identifier)

            def fetch(self, filters=None, page=1, page_size=100) -> QueryResult[User]:
                ...
    """

    #################################################
    # Class Attributes
    #################################################
    _name: str = "DataProvider"
    _type: str = "DataProvider"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        connection_config: Optional[Dict[str, Any]] = None,
        auto_connect: bool = False,
    ) -> None:
        """
        Initialize the data provider.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param connection_config: Connection configuration parameters.
        :param auto_connect: If True, automatically connect on initialization.
        """
        # Initialize the base DataModule
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
        )

        # Initialize provider status and connection config
        self._provider_status: ProviderStatus = ProviderStatus.DISCONNECTED
        self._connection_config: Dict[str, Any] = {}

        # Connect if auto_connect is True
        if auto_connect:
            self.connect(**connection_config)

    #################################################
    # Getter & Setter Methods
    #################################################
    def get_provider_status(self) -> ProviderStatus:
        """
        Get the current provider status.

        :return: Current ProviderStatus enum value.
        """
        return self._provider_status

    def set_provider_status(self, status: ProviderStatus) -> None:
        """
        Set the current provider status.

        :param status: Desired ProviderStatus enum value.
        """
        self._provider_status = status

    def get_connection_config(self) -> Dict[str, Any]:
        """
        Get the current connection configuration.

        :return: Current connection configuration as a dictionary.
        """
        return self._connection_config.copy()

    def set_connection_config(self, config: Dict[str, Any]) -> None:
        """
        Set the connection configuration.

        :param config: New connection configuration as a dictionary.
        """
        self._connection_config = config.copy()

    #################################################
    # Connection Management
    #################################################
    def connect(self, **config: Any) -> None:
        """
        Establish connection to the data source.

        :param config: Connection configuration parameters.
        :raises ConnectionError: If connection fails.
        """
        try:
            self._connection_config.update(config)
            self.get_logger().info(
                f"[{self._name}] Connecting to data source..."
            )
            self._connect()
            self._provider_status = ProviderStatus.CONNECTED
            self.get_logger().info(
                f"[{self._name}] Successfully connected."
            )
        except Exception as e:
            self._provider_status = ProviderStatus.ERROR
            self.get_logger().error(
                f"[{self._name}] Connection failed: {e}"
            )
            raise ConnectionError(f"Failed to connect: {e}") from e

    def disconnect(self) -> None:
        """
        Close connection to the data source.
        """
        try:
            self.get_logger().info(
                f"[{self._name}] Disconnecting from data source..."
            )
            self._disconnect()
            self._provider_status = ProviderStatus.DISCONNECTED
            self.get_logger().info(
                f"[{self._name}] Successfully disconnected."
            )
        except Exception as e:
            self.get_logger().error(
                f"[{self._name}] Disconnect failed: {e}"
            )
            raise

    def is_connected(self) -> bool:
        """
        Check if the provider is currently connected.

        :return: True if connected, False otherwise.
        """
        return self._provider_status == ProviderStatus.CONNECTED

    @contextmanager
    def connection(self, **config: Any) -> Iterator["DataProvider[T]"]:
        """
        Context manager for automatic connection handling.

        :param config: Connection configuration parameters.
        :yields: The connected provider instance.

        Example:
            with provider.connection(host="localhost") as p:
                data = p.get_by_id("123")
        """
        self.connect(**config)
        try:
            yield self
        finally:
            self.disconnect()

    @abstractmethod
    def _connect(self) -> None:
        """
        Internal method to establish connection to the data source.
        Implement source-specific connection logic here.

        :raises Exception: If connection fails.
        """
        pass

    @abstractmethod
    def _disconnect(self) -> None:
        """
        Internal method to close connection to the data source.
        Implement source-specific disconnection logic here.
        """
        pass

    #################################################
    # Core Data Retrieval Methods
    #################################################
    @abstractmethod
    def fetch(
        self,
        *args,
        **kwargs,
    ) -> QueryResult[T]:
        """
        Abstract method to retrieve data from the data source.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :raises QueryError: If the query operation fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    #################################################
    # Optional Hook Methods
    #################################################
    @abstractmethod
    def validate(self, data: T) -> bool:
        """
        Validate data before processing.
        Override this method to implement custom validation logic.

        :param data: Data to validate.
        :return: True if valid, False otherwise.
        :raises ValidationError: If validation fails critically.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def transform(self, data: Any) -> T:
        """
        Transform raw data from the source into the target type T.
        Override this method to implement custom transformation logic.

        :param data: Raw data from the source.
        :return: Transformed data of type T.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    def health_check(self) -> bool:
        """
        Perform a health check on the data source connection.
        Override this method to implement source-specific health checks.

        :return: True if healthy, False otherwise.
        """
        return self.is_connected()

    #################################################
    # Utility Methods
    #################################################
    def fetch_or_raise(self, *args, **kwargs) -> QueryResult[T]:
        """
        Fetch data or raise an error if not found.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: The fetched data.
        :raises QueryError: If the data is not found.
        """
        result = self.fetch(*args, **kwargs)
        if result.is_empty():
            raise QueryError("Data not found.")
        return result

    def with_retry(
        self,
        method: Callable[[], T],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        parameters: dict = None,
    ) -> T:
        """
        Execute an operation with retry logic.

        :param method: Callable to execute.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Delay between retries in seconds.
        :param parameters: Parameters to pass to the method.
        :return: Result of the operation.
        :raises DataProviderError: If all retries fail.
        """
        # Initialize variables
        last_error: Optional[Exception] = None

        # Retry loop
        for attempt in range(max_retries):
            try:
                return method(**parameters)
            except Exception as e:
                last_error = e
                self.get_logger().warning(
                    f"[{self._name}] Attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

        # Raise error if all retries failed
        raise DataProviderError(
            f"Operation failed after {max_retries} attempts: {last_error}"
        ) from last_error


#######################################################################
# Asynchronous Data Provider Class
#######################################################################
class AsyncDataProvider(ABC, DataModule, Generic[T]):
    """
    Abstract base class for asynchronous data providers with standardized async API interface.

    This class provides a unified interface for retrieving data from various sources
    (APIs, databases, files, etc.) using async/await patterns. Subclasses must implement
    the abstract methods to provide source-specific data retrieval logic.

    Type Parameters:
        T: The type of data entity this provider handles.

    Example Usage:
        class AsyncUserProvider(AsyncDataProvider[User]):
            async def _connect(self) -> None:
                self._db = await Database.connect(...)

            async def get_by_id(self, identifier: str) -> Optional[User]:
                return await self._db.users.find_one(id=identifier)

            async def fetch(self, *args, **kwargs) -> QueryResult[User]:
                ...
    """

    #################################################
    # Class Attributes
    #################################################
    _name: str = "AsyncDataProvider"
    _type: str = "AsyncDataProvider"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        connection_config: Optional[Dict[str, Any]] = None,
        auto_connect: bool = False,
    ) -> None:
        """
        Initialize the async data provider.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param connection_config: Connection configuration parameters.
        :param auto_connect: If True, automatically connect on initialization.
        """
        # Initialize the base DataModule
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
        )

        # Initialize provider status and connection config
        self._provider_status: ProviderStatus = ProviderStatus.DISCONNECTED
        self._connection_config: Dict[str, Any] = {}

        # Connect if auto_connect is True
        if auto_connect:
            # Note: This would need to be awaited in practice
            # For now, we'll just set up the config
            self._connection_config = connection_config or {}

    #################################################
    # Getter & Setter Methods
    #################################################
    def get_provider_status(self) -> ProviderStatus:
        """
        Get the current provider status.

        :return: Current ProviderStatus enum value.
        """
        return self._provider_status

    def set_provider_status(self, status: ProviderStatus) -> None:
        """
        Set the current provider status.

        :param status: Desired ProviderStatus enum value.
        """
        self._provider_status = status

    def get_connection_config(self) -> Dict[str, Any]:
        """
        Get the current connection configuration.

        :return: Current connection configuration as a dictionary.
        """
        return self._connection_config.copy()

    def set_connection_config(self, config: Dict[str, Any]) -> None:
        """
        Set the connection configuration.

        :param config: New connection configuration as a dictionary.
        """
        self._connection_config = config.copy()

    #################################################
    # Connection Management (Async)
    #################################################
    async def connect(self, **config: Any) -> None:
        """
        Establish connection to the data source asynchronously.

        :param config: Connection configuration parameters.
        :raises ConnectionError: If connection fails.
        """
        try:
            self._connection_config.update(config)
            self.get_logger().info(
                f"[{self._name}] Connecting to data source..."
            )
            await self._connect()
            self._provider_status = ProviderStatus.CONNECTED
            self.get_logger().info(
                f"[{self._name}] Successfully connected."
            )
        except Exception as e:
            self._provider_status = ProviderStatus.ERROR
            self.get_logger().error(
                f"[{self._name}] Connection failed: {e}"
            )
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def disconnect(self) -> None:
        """
        Close connection to the data source asynchronously.
        """
        try:
            self.get_logger().info(
                f"[{self._name}] Disconnecting from data source..."
            )
            await self._disconnect()
            self._provider_status = ProviderStatus.DISCONNECTED
            self.get_logger().info(
                f"[{self._name}] Successfully disconnected."
            )
        except Exception as e:
            self.get_logger().error(
                f"[{self._name}] Disconnect failed: {e}"
            )
            raise

    def is_connected(self) -> bool:
        """
        Check if the provider is currently connected.

        :return: True if connected, False otherwise.
        """
        return self._provider_status == ProviderStatus.CONNECTED

    @contextmanager
    def connection(self, **config: Any) -> Iterator["AsyncDataProvider[T]"]:
        """
        Synchronous context manager for automatic connection handling.
        Note: For async context management, use async_connection() instead.

        :param config: Connection configuration parameters.
        :yields: The connected provider instance.

        Example:
            with provider.connection(host="localhost") as p:
                # Use synchronous methods only
                pass
        """
        # This is a synchronous context manager for compatibility
        # In practice, you'd use async_connection() for async operations
        self._connection_config.update(config)
        try:
            yield self
        finally:
            pass  # Actual connection handled by async methods

    async def async_connection(self, **config: Any):
        """
        Asynchronous context manager for automatic connection handling.

        :param config: Connection configuration parameters.
        :yields: The connected provider instance.

        Example:
            async with provider.async_connection(host="localhost") as p:
                data = await p.fetch()
        """
        await self.connect(**config)
        try:
            yield self
        finally:
            await self.disconnect()

    #################################################
    # Abstract Methods - Must be implemented by subclasses
    #################################################
    @abstractmethod
    async def _connect(self) -> None:
        """
        Internal method to establish connection to the data source asynchronously.
        Implement source-specific connection logic here.

        :raises Exception: If connection fails.
        """
        pass

    @abstractmethod
    async def _disconnect(self) -> None:
        """
        Internal method to close connection to the data source asynchronously.
        Implement source-specific disconnection logic here.
        """
        pass

    @abstractmethod
    async def fetch(
        self,
        *args,
        **kwargs,
    ) -> QueryResult[T]:
        """
        Abstract method to retrieve data from the data source asynchronously.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :raises QueryError: If the query operation fails.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    #################################################
    # Optional Hook Methods (Async)
    #################################################
    async def validate(self, data: T) -> bool:
        """
        Validate data before processing asynchronously.
        Override this method to implement custom validation logic.

        :param data: Data to validate.
        :return: True if valid, False otherwise.
        :raises ValidationError: If validation fails critically.
        """
        return True

    async def transform(self, data: Any) -> T:
        """
        Transform raw data from the source into the target type T asynchronously.
        Override this method to implement custom transformation logic.

        :param data: Raw data from the source.
        :return: Transformed data of type T.
        """
        return data

    async def health_check(self) -> bool:
        """
        Perform a health check on the data source connection asynchronously.
        Override this method to implement source-specific health checks.

        :return: True if healthy, False otherwise.
        """
        return self.is_connected()

    #################################################
    # Utility Methods (Async)
    #################################################
    async def fetch_or_raise(self, *args, **kwargs) -> QueryResult[T]:
        """
        Fetch data or raise an error if not found asynchronously.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: The fetched data.
        :raises QueryError: If the data is not found.
        """
        result = await self.fetch(*args, **kwargs)
        if result.is_empty():
            raise QueryError("Data not found.")
        return result

    async def with_retry(
        self,
        operation: Callable[[], T],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> T:
        """
        Execute an operation with retry logic asynchronously.

        :param operation: Callable to execute.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Delay between retries in seconds.
        :return: Result of the operation.
        :raises DataProviderError: If all retries fail.
        """
        import asyncio

        # Initialize variables
        last_error: Optional[Exception] = None

        # Retry loop
        for attempt in range(max_retries):
            try:
                # If operation is async, await it
                if asyncio.iscoroutinefunction(operation):
                    return await operation()
                else:
                    return operation()
            except Exception as e:
                last_error = e
                self.get_logger().warning(
                    f"[{self._name}] Attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

        # Raise error if all retries failed
        raise DataProviderError(
            f"Operation failed after {max_retries} attempts: {last_error}"
        ) from last_error
