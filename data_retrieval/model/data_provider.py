#######################################################################
# Project: Data Retrieval Module
# File: data_provider.py
# Description: Abstract base class for data providers
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2026-01-18
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import (
    Any,
    Optional,
    Dict,
    Callable,
)

# Local Packages
from data_retrieval.model.data_module import DataModule
from data_retrieval.model.exceptions import (
    DataProviderConnectionError,
    DataMethodNotFoundError,
    ReturnDataTypeNotMatchedError,
)


#######################################################################
# Enums & Data Classes
#######################################################################
class DataProviderConnectionStatus(Enum):
    """
    Enumeration of provider connection states.
    """
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


#######################################################################
# Data Provider Class
#######################################################################
class DataProvider(DataModule):
    """
    Abstract base class for data providers with standardized synchronous API interface.

    This class provides a unified interface for retrieving data from various sources
    (APIs, databases, files, etc.). Subclasses must implement the abstract methods
    to provide source-specific data retrieval logic.
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "DataProvider"
    __type: str = "DataProvider"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        **config,
    ) -> None:
        """
        Initialize the data provider.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param config: Additional configuration parameters.
        """
        # Initialize the base DataModule
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
        )

        # Intialize DataProvider attributes
        self._config = config or {}
        self._connection = None
        self._data_methods = {}
        
        # Set initial status for the DataProvider instance
        self.set_status(DataProviderConnectionStatus.DISCONNECTED)

    #################################################
    # Getter & Setter Methods
    #################################################
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration dictionary.

        :return: The configuration dictionary.
        """
        return self._config

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set the configuration dictionary.

        :param config: The configuration dictionary.
        :return: None.
        """
        self._config = config
    
    def update_config(self, key: str, value: Any) -> None:
        """
        Update a specific configuration key-value pair.

        :param key: The configuration key to update.
        :param value: The new value for the configuration key.
        :return: None.
        """
        self._config.update({key: value})

    def get_connection(self) -> Any:
        """
        Get the connection object.

        :return: The connection object.
        """
        return self._connection

    def set_connection(self, connection: Any) -> None:
        """
        Set the connection object.

        :param connection: The connection object.
        :return: None.
        """
        self._connection = connection

    def get_data_methods(self) -> Dict[str, Any]:
        """
        Get the data methods dictionary.

        :return: The data methods dictionary.
        """
        return self._data_methods

    def get_data_method(self, data_point: str) -> Optional[Callable]:
        """
        Get a data method from the data methods dictionary.

        :param data_point: The name of the data method.
        :return: The data method.
        """
        return self._data_methods.get(data_point)

    def update_data_methods(self, new_methods: Dict[str, Callable]) -> None:
        """
        Update the data methods with new methods, merging with existing ones.
        
        :param new_methods: Dictionary of new data methods to add/update.
        :return: None.
        """
        self._data_methods.update(new_methods)

    def set_data_methods(self, data_methods: Dict[str, Any]) -> None:
        """
        Set the data methods dictionary.

        :param data_methods: The data methods dictionary.
        :return: None.
        """
        self._data_methods = data_methods

    def add_data_method(self, data_point: str, method: Any) -> None:
        """
        Add a data method to the data methods dictionary.

        :param data_point: The name of the data method.
        :param method: The data method.
        :return: None.
        """
        self._data_methods.update(
            {
                data_point: method,
            }
        )

    def delete_data_method(self, data_point: str) -> None:
        """
        Delete a data method from the data methods dictionary.

        :param data_point: The name of the data method to delete.
        :return: None.
        """
        if data_point in self._data_methods:
            del self._data_methods[data_point]
    
    #################################################
    # Connection Methods
    #################################################
    def is_connected(self) -> bool:
        """
        Check if the data provider is connected to the data source.

        :return: True if connected, False otherwise.
        """
        return self._connection is not None

    def connect(self, *args, **kwargs) -> None:
        """
        Safely Connect to the data source.

        :param args: Positional arguments for connection.
        :param kwargs: Keyword arguments for connection.
        :return: None.
        :raise ConnectionError: If connection fails.
        """
        try:
            self._connect(*args, **kwargs)
            self.set_status(status=DataProviderConnectionStatus.CONNECTED)
        except Exception as e:
            raise DataProviderConnectionError(f"Failed to connect to data source: {e}")

    @abstractmethod
    def _connect(self, *args, **kwargs):
        """
        Abstract method to connect to the data source.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def disconnect(self, *args, **kwargs) -> None:
        """
        Safely disconnect from the data source.

        :param args: Positional arguments for connection.
        :param kwargs: Keyword arguments for connection.
        :return: None.
        :raise ConnectionError: If connection fails.
        """
        try:
            self._disconnect(*args, **kwargs)
            self.set_status(status=DataProviderConnectionStatus.DISCONNECTED)
        except Exception as e:
            raise DataProviderConnectionError(f"Failed to disconnect from data source: {e}")

    @abstractmethod
    def _disconnect(self, *args, **kwargs):
        """
        Abstract method to disconnect from the data source.
        """
        raise NotImplementedError("Subclasses must implement this method")
            
    def refresh_connection(self, *args, **kwargs) -> None:
        """
        Refresh the connection.

        :param args: Positional arguments for connection.
        :param kwargs: Keyword arguments for connection.
        :return: None.
        :raise ConnectionError: If connection fails.
        """
        self.disconnect(*args, **kwargs)
        self.connect(*args, **kwargs)

    
    #################################################
    # Context Management
    #################################################
    def __enter__(self) -> "DataProvider":
        """
        Enter the runtime context related to this object. Automatically connects to the data source.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the runtime context related to this object. Automatically disconnects from the data source.
        """
        self.disconnect()

    #################################################
    # Core Instance Method: Fetch Data
    #################################################
    def fetch_data(self, data_point: str, return_data_type: type, *args, **kwargs) -> Any:
        """
        Base method to fetch data based on the data point and return type.

        :param data_point: str: The data point to fetch.
        :param return_data_type: type: The type of data to return.
        :param args: Tuple: Positional arguments for fetching data.
        :param kwargs: Dict: Keyword arguments for fetching data.
        :return: The fetched data.
        """
        # Extract the corresponding data method
        data_method = self.get_data_method(data_point=data_point)
        if data_method is None:
            raise DataMethodNotFoundError(f"Data method for data point '{data_point}' not found.")
        
        # Retrieve the data
        data = data_method(*args, **kwargs)

        # Check the return data type
        if not isinstance(data, return_data_type):
            raise ReturnDataTypeNotMatchedError(f"Data type mismatch. Expected {return_data_type}, got {type(data)}.")
        
        return data

