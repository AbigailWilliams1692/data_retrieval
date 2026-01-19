#######################################################################
# Project: Data Retrieval Module
# File: db_provider.py
# Description: Database data provider implementations
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-19
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import datetime
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Third-party Packages

# Local Packages
from data_retrieval.model.data_provider import DataProvider


#######################################################################
# Database Data Provider (Synchronous)
#######################################################################
class Database_DataProvider(DataProvider, ABC):
    """
    Base class for database data providers.

    This class extends the DataProvider base class to provide database-specific
    functionality for synchronous data retrieval operations. It serves as a
    foundation for implementing various database connection types and query
    operations.
    """

    ###################################################################
    # Class Attributes
    ###################################################################
    __name = "Database_DataProvider"
    __type = "Database_DataProvider"
        
    ###################################################################
    # Constructor Method
    ###################################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        **config,
    ) -> None:
        """
        Initialize the Database_DataProvider with the given parameters.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param config: Additional configuration parameters for the database connection.
        """
        # Super Initialize
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            **config    
        )

        # Prepare the data methods
        self.update_data_methods(
            {
                "sql_query": self.sql_query,
            }
        )

    ###################################################################
    # Core Instance Method: SQL Query
    ###################################################################
    @abstractmethod
    def sql_query(self, sql: str, *args, **kwargs) -> Any:
        """
        Posts the SQL query to the database and retrieves data accordingly.

        :param sql: the SQL query string.
        :return: the queried data.
        """
        raise NotImplementedError("Subclasses must implement sql_query method.")

    def format_sql_query(self, sql: str, params: Dict[str, Any]) -> str:
        """
        Format the SQL query string with the given key-value pairs.

        :param sql: the SQL query template string with placeholders.
        :param params: Dict[str, Any]: a Dictionary of key-value pairs used to parametrize the SQL query.
        :return: the formatted SQL query string. 
        """
        for key, value in params.items():
            placeholder = ":" + key

            # Covert the value to string based on its type
            if isinstance(value, str):
                value_to_replace = "'" + str(value) + "'"
            elif isinstance(value, (int, float)):
                value_to_replace = str(value)
            elif isinstance(value, datetime.date):
                value_to_replace = "'" + value.strftime("%Y-%m-%d") + "'"
            elif isinstance(value, List):
                value_to_replace = "'" + self.stringify_a_list_of_items_with_apostrophe(item_list=value) + "'"
            else:
                raise TypeError(f"Unsupported value type: {type(value)} for parameter '{key}'")

            # Replace all the placeholders in the SQL string
            sql = sql.replace(placeholder, value_to_replace, count=-1)

        return sql

    ###################################################################
    # Utility Methods
    ###################################################################
    @staticmethod
    def stringify_a_list_of_items_with_apostrophe(item_list: List[Any]) -> str:
        """
        Convert a list of items into a comma-separated string with each item wrapped in apostrophes.
        
        :param item_list: List of items to convert.
        :return: String representation of items wrapped in apostrophes and separated by commas.
        """
        item_str_list = [f"'{str(item)}'" for item in item_list]
        return ",".join(item_str_list)
