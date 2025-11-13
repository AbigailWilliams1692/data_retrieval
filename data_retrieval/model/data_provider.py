################################################
# Project: Data Retrieval Module
# File: data_provider.py
# Description: Abstract base class for data providers
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
from typing import Any

# Local Packages
from data_retrieval.log import get_logger
from data_retrieval.model.data_module import DataModule


#################################################
# Logger
#################################################
_logger = get_logger(name=__name__, log_level=logging.DEBUG)


#################################################
# Class Definition
#################################################
class DataProvider(DataModule, ABC):
    """Data Provider Abstract Base Class. Provides the interface for all data providers."""

    #################################################
    # Class Attributes
    #################################################
    name: str = "BaseDataProvider"
    type: str = "DataProvider"

    #################################################
    # Constructor
    #################################################
    def __init__(self, data_provider_id: str = None, logger: logging.Logger = _logger) -> None:
        """
        Constructor method.

        :param data_provider_id: str: Unique identifier for the data provider.
        :param logger: logging.Logger: Logger instance for logging.
        """
        # Super Constructor
        super().__init__(instance_id=data_provider_id, logger=logger)

    #################################################
    # Abstract Methods
    #################################################
    @abstractmethod
    async def fetch_data(self, data_name: str, data_type: type, *args, **kwargs) -> Any:
        """
        Abstract method to fetch data based on a query.

        :param data_name: str: The name of the data point to fetch.
        :param data_type: type: The expected type of the data to be fetched.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: Any: The fetched data as a dictionary.
        """
        raise NotImplementedError("Subclasses must implement this method.")
