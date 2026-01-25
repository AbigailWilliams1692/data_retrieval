######################################################################
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
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

# Third-Party Packages
from forex_python.converter import CurrencyCodes
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter

# Local Packages
from data_retrieval.foreign_exchange.forex_data_provider_base import Forex_DataProvider_Base
from data_retrieval.utils.date_utils import populate_dates_in_between


#######################################################################
# Forex Python Data Provider Class
#######################################################################
class ForexPython_DataProvider(Forex_DataProvider_Base):
    """
    Forex Python Data Provider Class
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "ForexPython_DataProvider"
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
        
        # Connect to the data source
        self.connect()
    
    #################################################
    # Connection Methods
    #################################################
    def _connect(self) -> None:
        """
        Connect to the data source.
        """
        self.set_connection(
            {
                "currency_codes": CurrencyCodes(),
                "currency_rates": CurrencyRates(),
                "btc_converter": BtcConverter(),
            }
        )
    
    def _disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        self.set_connection(None)

    #################################################
    # Core Instance Methods
    #################################################
    def get_exchange_rate_on_spot(
        self, 
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
        # Get the connection
        currency_rates = self.get_connection().get("currency_rates")
        
        # Get the exchange rate
        return currency_rates.get_rate(base_cur=base_currency, dest_cur=target_currency, date_obj=fx_datetime)
    
    def get_exchange_rates_historical(
        self,
        base_currency: str, 
        target_currencies: List[str], 
        fx_datetime_start: Union[datetime.datetime, datetime.date],
        fx_datetime_end: Union[datetime.datetime, datetime.date],
        *args,
        **kwargs,
    ) -> Dict[datetime.date, Dict[str, Optional[float]]]:
        """
        Get the exchange rates for a given currency pair on the current date.
        
        :param base_currency: The base currency code (e.g., 'USD').
        :param target_currencies: The target currency codes (e.g., ['EUR', 'GBP']).
        :param fx_datetime_start: The start timestamp for the exchange rate. (could be datetime or date)
        :param fx_datetime_end: The end timestamp for the exchange rate. (could be datetime or date)
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The exchange rates as a dictionary.
        """
        # Initialize the exchange rates container
        exchange_rates = {}

        # Get the connection
        currency_rates = self.get_connection().get("currency_rates")

        # Iterate through the date list and get the exchange rates for each date
        date_list = populate_dates_in_between(start_date=fx_datetime_start, end_date=fx_datetime_end, interval=1)
        for date in date_list:
            raw_record = currency_rates.get_rates(base_cur=base_currency, date_obj=date)
            exchange_rate_record = {
                f"{base_currency}/{target_currency}": raw_record.get(target_currency, None)
                for target_currency in target_currencies
            }
            exchange_rates[date] = exchange_rate_record
        
        return exchange_rates
        