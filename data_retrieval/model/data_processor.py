################################################
# Project: Data Retrieval Module
# File: data_processor.py
# Description: Abstract base class for data processors
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
class DataProcessor(DataModule, ABC):
    """Data Processor Abstract Base Class. Provides the interface for all data processor."""

    #################################################
    # Class Attributes
    #################################################
    name: str = "BaseDataProcessor"
    type: str = "DataProcessor"

    #################################################
    # Constructor
    #################################################
    def __init__(self, data_processor_id: str = None, logger: logging.Logger = _logger) -> None:
        """
        Constructor method.

        :param data_processor_id: str: Unique identifier for the data provider.
        :param logger: logging.Logger: Logger instance for logging.
        """
        # Super Constructor
        super().__init__(instance_id=data_processor_id, logger=logger)

    #################################################
    # Abstract Methods
    #################################################
    @abstractmethod
    async def process_data(self, data_name: str, data: Any, *args, **kwargs) -> Any:
        """
        Abstract method to process data.

        :param data_name: The name of the data to be processed.
        :param data: The input data to be processed.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The processed data.
        """
        raise NotImplementedError("Subclasses must implement this method.")
