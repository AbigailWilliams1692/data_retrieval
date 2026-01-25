#######################################################################
# Project: Data Retrieval Module
# File: forex_data_provider_wrapper.py
# Description: Forex Data Provider Wrapper
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
from typing import (
    Any,
    Dict, 
    List, 
    Optional,
    Union,
)

# Third-party Packages

# Local Packages
from data_retrieval.model import DataProvider_Wrapper
from data_retrieval.foreign_exchange.forex_data_provider_base import Forex_DataProvider_Base
from data_retrieval.foreign_exchange.forex_python_data_provider import ForexPython_DataProvider


#######################################################################
# Forex Data Provider (Synchronous)
#######################################################################
class Forex_DataProvider_Wrapper(DataProvider_Wrapper):
    """
    Foreign Exchange Data Provider Wrapper.
    
    This class provides a standard wrapper interface for retrieving Foreign Exchange data from various sources.
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "Forex_DataProvider_Wrapper"
    __type: str = "DataProvider_Wrapper"
    __valid_data_sources = [
        "forex-python",
        "exchange_rate_api",
    ]
    __valid_data_source_mapping = {
        "forex-python": ForexPython_DataProvider,
        "exchange_rate_api": None,
    }

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        data_source: str = "forex-python",
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        **config,
    ) -> None:
        """
        Initialize the Forex Data Provider.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param data_methods: Dictionary of data retrieval methods.
        :param config: Additional configuration parameters.
        """
        # Initialize the base DataProvider
        super().__init__(
            data_source=data_source,
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            valid_data_sources=self.__valid_data_sources,
            valid_data_source_mapping=self.__valid_data_source_mapping,
            **config,
        )

    #################################################
    # Core Instance Method: Get Exchange Rate
    #################################################
    def get_exchange_rate_on_spot(
        self, 
        base_currency: str, 
        target_currency: str, 
        fx_datetime: Optional[Union[datetime.datetime, datetime.date]] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Get the exchange rate for a given currency pair on the current date.
        
        :param base_currency: The base currency code (e.g., 'USD').
        :param target_currency: The target currency code (e.g., 'EUR').
        :param fx_datetime: The timestamp for the exchange rate. (could be datetime or date)
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The exchange rate as a float.
        """
        return self.fetch_data(
            data_point="exchange_rate_on_spot",
            return_data_type=float,
            base_currency=base_currency,
            target_currency=target_currency,
            fx_datetime=fx_datetime,
            *args,
            **kwargs,
        )

    def get_exchange_rates_historical(
        self,
        base_currency: str, 
        target_currencies: List[str], 
        fx_datetime_start: Union[datetime.datetime, datetime.date],
        fx_datetime_end: Union[datetime.datetime, datetime.date],
        *args,
        **kwargs,
    ) -> Any:
        """
        Get the exchange rates for a base currency and multiple target currencies over a time range.
        
        :param base_currency: The base currency code (e.g., 'USD').
        :param target_currencies: The target currency codes (e.g., ['EUR', 'GBP']).
        :param fx_datetime_start: The start timestamp for the exchange rate. (could be datetime or date)
        :param fx_datetime_end: The end timestamp for the exchange rate. (could be datetime or date)
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The exchange rate as a float.
        """
        return self.fetch_data(
            data_point="exchange_rate_historical",
            return_data_type=Dict,
            base_currency=base_currency,
            target_currencies=target_currencies,
            fx_datetime_start=fx_datetime_start,
            fx_datetime_end=fx_datetime_end,
            *args,
            **kwargs,
        )   
    