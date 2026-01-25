#######################################################################
# Project: Data Retrieval Module
# File: forex_data_provider_base.py
# Description: Forex Data Provider Base
# Author: AbigailWilliams1692
# Created: 2026-01-24
# Updated: 2026-01-24
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import datetime
import logging
from abc import ABC, abstractmethod
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

# Third-Party Packages

# Local Packages
from data_retrieval.model import DataProvider


#######################################################################
# Base Class
#######################################################################
class Forex_DataProvider_Base(DataProvider, ABC):
    """
    Forex Data Provider Base Class
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "Forex_DataProvider_Base"
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
            **config
        )

        # Update the data methods
        self.update_data_methods(
            new_methods={
                "exchange_rate_on_spot": self.get_exchange_rate_on_spot,
                "exchange_rate_historical": self.get_exchange_rates_historical,
            }
        )

    #################################################
    # Connection Methods
    #################################################
    @abstractmethod
    def _connect(self) -> None:
        """
        Connect to the data source.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def _disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        raise NotImplementedError("Subclasses must implement this method")

    #################################################
    # Core Instance Methods
    #################################################
    @abstractmethod
    def get_exchange_rate_on_spot(self, 
        base_currency: str, 
        target_currency: str, 
        fx_datetime: Optional[Union[datetime.datetime, datetime.date]] = None,
        *args,
        **kwargs,
    ) -> float:
        """
        Get the exchange rate for a given currency pair on the current date.
        
        :param base_currency: The base currency code (e.g., 'USD').
        :param target_currency: The target currency code (e.g., 'EUR').
        :param fx_datetime: The timestamp for the exchange rate. (could be datetime or date)
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The exchange rate as a float.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_exchange_rates_historical(
        self,
        base_currency: str, 
        target_currencies: List[str], 
        fx_datetime_start: Union[datetime.datetime, datetime.date],
        fx_datetime_end: Union[datetime.datetime, datetime.date],
        *args,
        **kwargs,
    ) -> Dict[str, Dict[str, float]]:
        """
        Get the exchange rates for a base currency and multiple target currencies over a time range.
        
        :param base_currency: The base currency code (e.g., 'USD').
        :param target_currencies: The target currency codes (e.g., ['EUR', 'GBP']).
        :param fx_datetime_start: The start timestamp for the exchange rate. (could be datetime or date)
        :param fx_datetime_end: The end timestamp for the exchange rate. (could be datetime or date)
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A dictionary mapping dates to exchange rates.
        """
        raise NotImplementedError("Subclasses must implement this method")

