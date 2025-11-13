###############################################
# Project: Data Retrieval Module
# File: data_manager.py
# Description: Abstract base class for data managers
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2025-11-13
#################################################

#################################################
# Import Packages
#################################################
# Standard Packages
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Local Packages
from data_retrieval.log import get_logger
from data_retrieval.model.data_module import DataModule
from data_retrieval.model.data_provider import DataProvider
from data_retrieval.model.data_processor import DataProcessor
from data_retrieval.model.data_storer import DataStorer

#################################################
# Logger
#################################################
_logger = get_logger(name=__name__, log_level=logging.DEBUG)


#################################################
# Class Definition
#################################################
class DataManager(DataModule, ABC):
    """
    Data Manager Abstract Base Class. Provides the interface for all data managers.
    Data Managers coordinate data retrieval, processing, and storage.
    """

    #################################################
    # Class Attributes
    #################################################
    name: str = "BaseDataManager"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        data_manager_id: str = None,
        data_providers: List[DataProvider] = None,
        data_processors: List[DataProcessor] = None,
        data_storers: List[DataStorer] = None,
        logger: logging.Logger = _logger,
    ) -> None:
        """
        Constructor method.

        :param data_manager_id: str: Unique identifier for the data manager.
        :param data_providers: List[DataProvider]: List of data provider instances.
        :param data_processors: List[DataProcessor]: List of data processor instances.
        :param data_storers: List[DataStorer]: List of data storer
        :param logger: logging.Logger: Logger instance for logging.
        """
        # Super Constructor
        super().__init__(instance_id=data_manager_id, logger=logger)

        # Initialize Components
        self.data_providers = self.initialize_components(components=data_providers)
        self.data_processors = self.initialize_components(components=data_processors)
        self.data_storers = self.initialize_components(components=data_storers)
        self.data_modules = self.initialize_components_by_id(components=data_providers+data_processors+data_storers)

    #################################################
    # Concrete Methods
    #################################################
    @staticmethod
    def initialize_components(components: List[DataModule]) -> Dict:
        """
        Initialize the components into Hash lists classified by the class names of the modules

        :param components: List[DataModule]: List of data modules to initialize.
        :return component_dict: Dict: Dictionary of components classified by class names.
        """
        # Initialize dictionary container
        component_dict = {}

        # Loop through components and classify them by class name
        for component in components or []:
            class_name = component.name
            if class_name not in component_dict:
                component_dict[class_name] = []
            component_dict[class_name].append(component)
        return component_dict

    @staticmethod
    def initialize_components_by_id(components: List[DataModule]) -> Dict:
        """
        Initialize the components into Hash lists classified by the instance IDs of the modules

        :param components: List[DataModule]: List of data modules to initialize.
        :return component_dict: Dict: Dictionary of components that can be directly queried by their IDs.
        """
        # Initialize dictionary container
        component_dict = {data_module.get_instance_id(): data_module for data_module in components}
        return component_dict

    def get_data_module(self, data_module_type: str, data_module_name: str) -> Optional[DataModule]:
        """
        Retrieve a data module by its type and name.

        :param data_module_type: str: The type of the data module (e.g., DataProvider, DataProcessor, DataStorer).
        :param data_module_name: str: The name of the data module class.
        :return: DataModule: The requested data module, or None if not found.
        """
        # Select the appropriate data module list based on type
        if data_module_type == DataProvider.type:
            data_module_list = self.data_providers.get(data_module_name, [])
        elif data_module_type == DataProcessor.type:
            data_module_list = self.data_processors.get(data_module_name, [])
        elif data_module_type == DataStorer.type:
            data_module_list = self.data_storers.get(data_module_name, [])
        else:
            raise ValueError(f"Unknown data module type: {data_module_type}")
        return self.get_data_module_from_list(data_module_list=data_module_list)

    @staticmethod
    def get_data_module_from_list(data_module_list: List[DataModule]) -> Optional[DataModule]:
        """
        Retrieve the first data module that is not preoccupied.

        :param data_module_list: List[DataModule]: List of data modules to search.
        :return: DataModule: The first available data module, or None if all are preoccupied.
        """
        for data_module in data_module_list:
            if not data_module.get_status():
                return data_module
        return None

    def get_data_module_by_id(self, data_module_id: str) -> Optional[DataModule]:
        """
        Retrieve a data module by its instance ID.

        :param data_module_id: str: The instance ID of the data module.
        :return: DataModule: The requested data module, or None if not found.
        """
        return self.data_modules.get(data_module_id, None)

    #################################################
    # Abstract Methods
    #################################################
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Abstract method to perform the data management work.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: Any.
        """
        raise NotImplementedError("Subclasses must implement this method.")
