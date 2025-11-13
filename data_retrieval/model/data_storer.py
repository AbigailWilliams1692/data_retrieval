################################################
# Project: Data Retrieval Module
# File: data_storer.py
# Description: Abstract base class for data storers
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


#################################################
# Logger
#################################################
_logger = get_logger(name=__name__, log_level=logging.DEBUG)


#################################################
# Class Definition
#################################################
class DataStorer(ABC):
    """Data Storer Abstract Base Class. Provides the interface for all data storers."""

    #################################################
    # Class Attributes
    #################################################
    name: str = "BaseDataStorer"

    #################################################
    # Constructor
    #################################################
    def __init__(self, data_storer_id: str = None, logger: logging.Logger = _logger) -> None:
        """
        Constructor method.

        :param: data_storer_id: str: Unique identifier for the data provider.
        :param: logger: logging.Logger: Logger instance for logging.
        """
        super().__init__(instance_id=data_storer_id, logger=logger)

    #################################################
    # Abstract Methods
    #################################################
    @abstractmethod
    def save_data(self, data_name: str, data: Any) -> Any:
        """Abstract method to save data.

        :param data_name: str: The name of the data to be saved.
        :param data: Any: Data to be saved.
        :return: Any: Result of the save operation.
        """
        raise NotImplementedError("Subclasses must implement save_data method.")
