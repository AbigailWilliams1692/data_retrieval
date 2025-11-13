################################################
# Project: Data Retrieval Module
# File: data_module.py
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

# Local Packages
from data_retrieval.log import get_logger


#################################################
# Logger
#################################################
_logger = get_logger(name=__name__, log_level=logging.DEBUG)


#################################################
# Class Definition
#################################################
class DataModule(ABC):
    """Data Module Abstract Base Class. Provides the interface for all data modules."""

    #################################################
    # Class Attributes
    #################################################
    name: str = "BaseDataModule"

    #################################################
    # Constructor
    #################################################
    def __init__(self, instance_id: str = None, logger: logging.Logger = _logger) -> None:
        """
        Constructor method.

        :param instance_id: str: Unique identifier for the data module instance.
        :param logger: logging.Logger: Logger instance for logging.
        """
        # DataProvider ID
        if instance_id is None:
            self.instance_id = str(id(self))
        else:
            self.instance_id = instance_id

        # Logger
        self.logger = logger
