#######################################################################
# Project: Data Retrieval Module
# File: data_provider_wrapper.py
# Description: Wrapper class for managing multiple data providers
# Author: AbigailWilliams1692
# Created: 2026-01-24
# Updated: 2026-01-24
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from typing import (
    Any,
    Optional,
    Dict,
    List,
    Type,
)

# Local Packages
from data_retrieval.model.data_module import DataModule
from data_retrieval.model.data_provider import DataProvider
from data_retrieval.model.exceptions import (
    DataProviderError,
    DataProviderNotFoundError,
    DataProviderInitializationError,
    DataProviderWrapperConnectionError,
)


#######################################################################
# Data Provider Wrapper Connection Status
#######################################################################
class DataProviderWrapperConnectionStatus:
    """
    Connection status for DataProvider_Wrapper.
    """
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


#######################################################################
# Data Provider Wrapper Class
#######################################################################
class DataProvider_Wrapper(DataModule):
    """
    Wrapper class for managing multiple data providers with a unified interface.

    This class allows switching between different data providers (data sources)
    for fetching the same category of data. It mimics the DataProvider interface
    while providing the flexibility to choose which underlying provider to use.
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "DataProvider_Wrapper"
    __type: str = "DataProvider_Wrapper"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        data_source: str,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        valid_data_sources: Optional[List[str]] = None,
        valid_data_source_mapping: Optional[Dict[str, Type[DataProvider]]] = None,
        **config,
    ) -> None:
        """
        Initialize the data provider wrapper.

        :param data_source: The data source name to use for fetching data.
        :param instance_id: Unique identifier for this wrapper instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the wrapper.
        :param config: Additional configuration parameters.
        """
        # Initialize the base DataModule
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
        )

        # Initialize DataProvider_Wrapper attributes
        ## Valid data sources and mappings
        self.__valid_data_sources = valid_data_sources
        self.__valid_data_source_mapping = valid_data_source_mapping

        ## Other attributes
        self._config = config or {}
        self._data_source: Optional[str] = data_source
        self._data_provider: Optional[DataProvider] = self._initialize_data_provider_instance(data_source=data_source)

        # Set initial status for the DataProvider_Wrapper instance
        self.set_status(DataProviderWrapperConnectionStatus.DISCONNECTED)

    #################################################
    # Getter & Setter Methods
    #################################################
    def get_valid_data_sources(self) -> List[str]:
        """
        Get the list of valid data sources.

        :return: The list of valid data sources.
        """
        return self.__valid_data_sources

    def set_valid_data_sources(self, valid_data_sources: List[str]) -> None:
        """
        Set the list of valid data sources.

        :param valid_data_sources: The list of valid data sources to set.
        :return: None.
        """
        self.__valid_data_sources = valid_data_sources

    def add_valid_data_source(self, valid_data_source: str) -> None:
        """
        Add a valid data source to the list of valid data sources.

        :param valid_data_source: The valid data source to add.
        :return: None.
        """
        self.__valid_data_sources.append(valid_data_source)

    def remove_valid_data_source(self, valid_data_source: str) -> None:
        """
        Remove a valid data source from the list of valid data sources.

        :param valid_data_source: The valid data source to remove.
        :return: None.
        """
        self.__valid_data_sources.remove(valid_data_source)

    def get_valid_data_source_mapping(self) -> Dict[str, Type[DataProvider]]:
        """
        Get the mapping of valid data sources to their corresponding DataProvider classes.

        :return: The mapping of valid data sources to their corresponding DataProvider classes.
        """
        return self.__valid_data_source_mapping

    def set_valid_data_source_mapping(self, valid_data_source_mapping: Dict[str, Type[DataProvider]]) -> None:
        """
        Set the mapping of valid data sources to their corresponding DataProvider classes.

        :param valid_data_source_mapping: The mapping of valid data sources to their corresponding DataProvider classes.
        :return: None.
        """
        self.__valid_data_source_mapping = valid_data_source_mapping

    def update_valid_data_source_mapping(self, valid_data_source: str, data_provider_class: Type[DataProvider]) -> None:
        """
        Update the mapping of a valid data source to its corresponding DataProvider class.

        :param valid_data_source: The valid data source to update.
        :param data_provider_class: The DataProvider class to map to the valid data source.
        :return: None.
        """
        self.__valid_data_source_mapping[valid_data_source] = data_provider_class

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

    def get_data_source(self) -> Optional[str]:
        """
        Get the current data source.

        :return: The current data source name.
        """
        return self._data_source

    def set_data_source(self, data_source: str) -> None:
        """
        Validate the data source first and set the data source to use for fetching data.

        :param data_source: The name of the data source to use.
        :return: None.
        :raises KeyError: If the data source is not registered.
        """
        if not self.validate_data_source(data_source):
            raise KeyError(f"Data source '{data_source}' is not valid.")
        self._data_source = data_source

    def get_data_provider(self) -> Optional[DataProvider]:
        """
        Get the current data provider.

        :return: The current data provider instance.
        """
        return self._data_provider

    def set_data_provider(self, data_provider: DataProvider) -> None:
        """
        Set the current data provider.

        :param data_provider: The DataProvider instance to set.
        :return: None.
        """
        self._data_provider = data_provider

    #################################################
    # Data Provider Management Methods
    #################################################
    def switch_data_provider(self, data_source: str) -> None:
        """
        Switch to another data provider that has already been registered.

        :param data_source: The data source name to register.
        :return: None.
        """
        if data_source == self.get_data_source():
            raise ValueError(f"Data source '{data_source}' is already the current data source.")
        elif self.validate_data_source(data_source=data_source):
            self.set_data_source(data_source=data_source)
            self.set_data_provider(
                data_provider=self._initialize_data_provider_instance(data_source=data_source)
            )

    def register_data_provider(self, data_source: str, data_provider_class: Type[DataProvider]) -> None:
        """
        Register a new data provider class.

        :param data_source: The data source name to register.
        :param data_provider_class: The DataProvider class to register.
        :return: None.
        """
        self.__valid_data_sources[data_source] = data_provider_class

    def unregister_data_provider(self, data_source: str) -> None:
        """
        Unregister a data provider class.

        :param data_source: The data source name to unregister.
        :return: None.
        """
        if data_source in self.__valid_data_sources:
            del self.__valid_data_sources[data_source]

    def _initialize_data_provider_instance(self, data_source: Optional[str] = None) -> DataProvider:
        """
        Initialize the data provider as the data source instance.

        :param data_source: The data source to use. If None, uses the current data source.
        :return: The initialized data provider instance.
        """
        # Check if data source is None.
        if data_source is None:
            data_source = self.get_data_source()

        # Get the data provider class from the mapping
        data_provider_class = self.__valid_data_source_mapping.get(data_source, None)
        
        # Check if the data provider class is found
        if data_provider_class is None:
            raise DataProviderNotFoundError(
                f"No data provider found for data source: '{data_source}'."
            )

        # Initialize the data provider instance
        try:
            data_provider_instance = data_provider_class(
                log_level=self.get_log_level(),
                **self.get_config(),
            )
        except DataProviderError as e:
            raise e
        except Exception as e:
            raise DataProviderInitializationError(
                f"Failed to initialize data provider for data source: '{data_source}'. Error: {str(e)}"
            )

        return data_provider_instance
            
    #################################################
    # Connection Methods
    #################################################
    def is_connected(self) -> bool:
        """
        Check if the specified data provider is connected.

        :return: True if connected, False otherwise.
        """
        data_provider = self.get_data_provider()
        if data_provider is None:
            raise DataProviderNotFoundError(
                f"No data provider found for data source: '{self.get_data_source()}'."
            )
        return data_provider.is_connected()

    def connect(self) -> None:
        """
        Connect to the specified data provider.
        """
        try:
            data_provider = self.get_data_provider()
            if data_provider is None:
                raise DataProviderNotFoundError(
                    f"No data provider found for data source: '{self.get_data_source()}'."
                )
            data_provider.connect()
            self.set_status(DataProviderWrapperConnectionStatus.CONNECTED)
        except DataProviderError as e:
            raise e
        except Exception as e:
            raise DataProviderWrapperConnectionError(
                f"Failed to connect to data provider for data source: '{self.get_data_source()}'. Error: {str(e)}"
            )

    def disconnect(self) -> None:
        """
        Disconnect from the specified data provider.
        """
        try:
            data_provider = self.get_data_provider()
            if data_provider is None:
                raise DataProviderNotFoundError(
                    f"No data provider found for data source: '{self.get_data_source()}'."
                )
            data_provider.disconnect()
            self.set_status(DataProviderWrapperConnectionStatus.DISCONNECTED)
        except DataProviderError as e:
            raise e
        except Exception as e:
            raise DataProviderWrapperConnectionError(
                f"Failed to disconnect from data provider for data source: '{self.get_data_source()}'. Error: {str(e)}"
            )

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
    def fetch_data(
        self,
        data_point: str,
        return_data_type: type,
        *args,
        **kwargs,
    ) -> Any:
        """
        Fetch data from the specified data source.
 
        :param data_point: The data point to fetch.
        :param return_data_type: The expected return data type.
        :param args: Positional arguments for fetching data.
        :param kwargs: Keyword arguments for fetching data.
        :return: The fetched data.
        :raises DataProviderNotFoundError: If no provider is found for the data source.
        :raises DataMethodNotFoundError: If the data method is not found.
        :raises ReturnDataTypeNotMatchedError: If the return data type does not match.
        """
        # Get the data provider for the current data source
        data_provider = self.get_data_provider()

        # Check if the data provider exists
        if data_provider is None:
            raise DataProviderNotFoundError(
                f"No data provider found for data source '{self.get_data_source()}'."
            )

        # Fetch the data
        data: Any = data_provider.fetch_data(
            data_point=data_point, 
            return_data_type=return_data_type, 
            *args, 
            **kwargs
        )
        
        return data

    #################################################
    # Utility Methods
    #################################################
    def validate_data_source(self, data_source: str) -> bool:
        """
        Validate if the provided data source is supported.
        
        :param data_source: The data source to validate.
        :return: True if the data source is valid, False otherwise.
        """
        print(self.get_valid_data_sources())
        return data_source in self.__valid_data_sources
