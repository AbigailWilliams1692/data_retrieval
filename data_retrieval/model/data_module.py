#######################################################################
# Project: Data Retrieval Module
# File: data_module.py
# Description: Abstract base class for aall data modules
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2026-01-18
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from abc import ABC
from typing import Any, Optional

# Local Packages


#################################################
# Class Definition
#################################################
class DataModule(ABC):
    """
    Data Module Abstract Base Class. Provides the interface for all data modules.
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "BaseDataModule"
    __type: str = "DataModule"

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
    ) -> None:
        """
        Constructor method.

        :param instance_id: str: Unique identifier for the data module instance.
        :param logger: logging.Logger: Logger instance for logging.
        """
        # DataProvider ID
        self._instance_id = instance_id or id(self)
        

        # Log Level
        self._log_level = log_level

        # Logger
        self._logger = logger or self.refresh_logger()

        # Status
        self._status = None

    #################################################
    # Getter & Setter Methods
    #################################################
    def get_name(self) -> str:
        """
        Get the name of the data module.

        :return: str: Name of the data module.
        """
        return self.__name

    def get_type(self) -> str:
        """
        Get the type of the data module.

        :return: str: Type of the data module.
        """
        return self.__type


    def get_instance_id(self) -> str:
        """
        Get the unique identifier of the data module instance.

        :return: str: Unique identifier of the data module instance.
        """
        return self._instance_id

    def set_instance_id(self, instance_id: str) -> None:
        """
        Set the unique identifier of the data module instance.

        :param instance_id: str: Unique identifier of the data module instance.
        """
        self._instance_id = instance_id

    def get_logger(self) -> logging.Logger:
        """
        Get the logger instance.

        :return: logging.Logger: Logger instance.
        """
        return self._logger

    def set_logger(self, logger: logging.Logger) -> None:
        """
        Set the logger instance.

        :param logger: logging.Logger: Logger instance.
        """
        self._logger = logger

    def refresh_logger(self) -> logging.Logger:
        """
        Refresh the logger instance.
        """
        logger = logging.getLogger(name=self.__class__.__name__)
        logger.setLevel(self._log_level)
        return logger

    def get_log_level(self) -> int:
        """
        Get the log level of the logger instance.

        :return: int: Log level of the logger instance.
        """
        return self._log_level
    
    def set_log_level(self, log_level: int) -> None:
        """
        Set the log level of the logger instance.

        :param log_level: int: Log level of the logger instance.
        """
        self._logger.setLevel(level=log_level)

    def get_status(self) -> Any:
        """Get the preoccupation status of the data module.

        :return: Any: Preoccupation status of the data module.
        """
        return self._status

    def set_status(self, status: Any) -> None:
        """
        Set the preoccupation status of the data module.

        :param status: Any: Preoccupation status of the data module.
        """
        self._status = status
