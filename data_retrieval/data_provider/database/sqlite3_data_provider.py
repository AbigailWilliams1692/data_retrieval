#!/usr/bin/env python3
########################################################################
# File: database_service.py
# Description: SQLite3 database data provider
# Author: AbigailWilliams1692
# Creation Date: 2026-01-29
# Version: 1.0.0
# License: MIT License
########################################################################

########################################################################
# Import Libraries
########################################################################
# Standard Packages
import logging
import sqlite3
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party Packages
from data_retrieval.data_provider.database.database_data_provider import (
    Database_DataProvider,
)


########################################################################
# SQLite3 Data Provider Class
########################################################################
class SQLite3FetchMode(str, Enum):
    """
    Enum for fetch modes.
    """
    ALL = "all"
    ONE = "one"
    MANY = "many"
    LAST_ID = "last_id"
    NONE = "none"


class SQLite3_DataProvider(Database_DataProvider):
    """
    SQLite3 data provider class.
    """

    ###################################################################
    # Class Attributes
    ###################################################################
    __name = "SQLite3_DataProvider"

    ###################################################################
    # Constructor Method
    ###################################################################
    def __init__(
        self,
        db_file_path: str,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        **config,
    ) -> None:
        """
        Initialize the DatabaseService with the given parameters.

        :param db_file_path: Path to the SQLite database file (.db).
        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the provider.
        :param config: Additional configuration parameters.
        """
        # Super Initialize
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            **config,
        )

        # Initialize the DatabaseService attributes
        ## Store the database path
        self._db_file_path = db_file_path
        ## Initialize the cursor
        self._cursor: Optional[sqlite3.Cursor] = None
        ## Connect to the datbase file
        self.connect()

        # Update data methods
        self.update_data_methods(
            new_methods={
                "execute": self.execute,
                "execute_many": self.execute_many,
                "fetch_one": self.fetch_one,
                "fetch_many": self.fetch_many,
                "fetch_all": self.fetch_all,
            }
        )
    
    ###################################################################
    # Getter & Setter Methods
    ###################################################################
    def get_db_file_path(self) -> str:
        """
        Get the database file path.

        :return: The path to the SQLite database file.
        """
        return self._db_file_path

    def set_db_file_path(self, db_file_path: str) -> None:
        """
        Set the database file path.

        :param db_file_path: The path to the SQLite database file.
        :return: None.
        """
        self._db_file_path = db_file_path

    def get_cursor(self) -> Optional[sqlite3.Cursor]:
        """
        Get the database cursor.

        :return: The SQLite cursor object.
        """
        return self._cursor

    def set_cursor(self, cursor: sqlite3.Cursor) -> None:
        """
        Set the database cursor.

        :param cursor: The SQLite cursor object.
        :return: None.
        """
        self._cursor = cursor

    ###################################################################
    # Connection Methods
    ###################################################################
    def _connect(self, *args, **kwargs) -> None:
        """
        Connect to the SQLite database.

        Creates a connection to the SQLite database file specified by db_file_path.
        If the file does not exist, SQLite will create it.

        :param args: Positional arguments (unused).
        :param kwargs: Keyword arguments (unused).
        :return: None.
        :raises sqlite3.Error: If connection fails.
        """
        # Connect to the database
        conn = sqlite3.connect(self.get_db_file_path())
        
        # Set row factory to return rows as sqlite3.Row objects
        conn.row_factory = sqlite3.Row
        
        # Set connection and cursor
        self.set_connection(connection=conn)
        self.set_cursor(conn.cursor())

    def _disconnect(self) -> None:
        """
        Disconnect from the SQLite database.

        Closes the cursor and connection to the database.

        :param args: Positional arguments (unused).
        :param kwargs: Keyword arguments (unused).
        :return: None.
        :raises sqlite3.Error: If disconnection fails.
        """
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

        conn = self.get_connection()
        if conn is not None:
            conn.close()
            self.set_connection(connection=None)

    ###################################################################
    # Core Instance Method: Execute
    ###################################################################
    def execute(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None,
        fetch_mode: str = SQLite3FetchMode.ALL,
        commit: bool = True,
        **kwargs,
    ) -> Any:
        """
        Execute a SQL query on the SQLite database.

        :param sql: The SQL query string to execute.
        :param params: Optional parameters for parameterized queries.
                       Can be a tuple for positional params or dict for named params.
        :param fetch: Fetch mode - "all", "one", "many", or "none".
                      - "all": Fetch all results (fetchall).
                      - "one": Fetch single result (fetchone).
                      - "many": Fetch specified number of results (fetchmany).
                      - "none": Don't fetch results (for INSERT/UPDATE/DELETE).
        :param commit: Whether to commit the transaction after execution.
        :param kwargs: Additional keyword arguments.
                       - fetch_size: Number of rows to fetch when fetch="many".
        :return: Query results based on fetch mode, or lastrowid for INSERT operations.
        :raises sqlite3.Error: If query execution fails.
        :raises ValueError: If invalid fetch mode is specified.
        """
        # Check if the database is connected
        self.check_db_connection()

        # Get the connection and the cursor
        conn = self.get_connection()
        cursor = self.get_cursor()

        # Execute the query with or without parameters
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        # Commit if requested
        if commit:
            conn.commit()

        # Fetch results based on mode
        if fetch_mode == "all":
            return cursor.fetchall()
        elif fetch_mode == "one":
            return cursor.fetchone()
        elif fetch_mode == "many":
            fetch_size = kwargs.get("fetch_size", 100)
            return cursor.fetchmany(fetch_size)
        elif fetch_mode == "last_id":
            return cursor.lastrowid
        elif fetch_mode == "none":
            return None
        else:
            raise ValueError(f"Invalid fetch mode: {fetch_mode}. Must be 'all', 'one', 'many', or 'none'.")

    def execute_many(
        self,
        sql: str,
        params_list: List[Union[Tuple, Dict[str, Any]]],
        fetch_mode: str = "all",
        commit: bool = True,
    ) -> None:
        """
        Execute a SQL statement on the SQLite database multiple times with different parameters.

        :param sql: The SQL statement to execute.
        :param params_list: List of parameter tuples or dicts.
        :param commit: Whether to commit the transaction (default: True).
        :return: None.
        """
        # Check if the database is connected
        self.check_db_connection()

        # Get the connection and the cursor
        conn = self.get_connection()
        cursor = self.get_cursor()

        # Execute the query with multiple parameter groups
        cursor.executemany(sql, params_list)

        # Commit if requested
        if commit:
            conn.commit()

        # Fetch results based on mode
        if fetch_mode == "all":
            return cursor.fetchall()
        elif fetch_mode == "one":
            return cursor.fetchone()
        elif fetch_mode == "many":
            fetch_size = kwargs.get("fetch_size", 100)
            return cursor.fetchmany(fetch_size)
        elif fetch_mode == "last_id":
            return cursor.lastrowid
        elif fetch_mode == "none":
            return None
        else:
            raise ValueError(f"Invalid fetch mode: {fetch_mode}. Must be 'all', 'one', 'many', or 'none'.")

    ###################################################################
    # Core Instance Methods: Fetch One/Many/All
    ###################################################################
    def fetch_one(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None,
    ) -> Optional[sqlite3.Row]:
        """
        Execute a SELECT query and fetch a single result.

        :param sql: The SQL SELECT query.
        :param params: Optional parameters for parameterized queries.
        :return: Single result row or None.
        """
        return self.execute(sql=sql, params=params, fetch="one")

    def fetch_many(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None,
        fetch_size: int = 100,
    ) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and fetch multiple results.

        :param sql: The SQL SELECT query.
        :param params: Optional parameters for parameterized queries.
        :param fetch_size: Number of rows to fetch (default: 100).
        :return: List of result rows.
        """
        return self.execute(sql=sql, params=params, fetch="many", fetch_size=fetch_size)

    def fetch_all(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None,
    ) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and fetch all results.

        :param sql: The SQL SELECT query.
        :param params: Optional parameters for parameterized queries.
        :return: List of all result rows.
        """
        return self.execute(sql=sql, params=params, fetch="all")

    ###################################################################
    # Core Instance Method: Commit
    ###################################################################
    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        self.check_db_connection()
        self.get_connection().commit()

    ###################################################################
    # Core Instance Method: Rollback
    ###################################################################
    def rollback(self) -> None:
        """
        Rollback the current transaction.

        :return: None.
        """
        self.check_db_connection()
        self.get_connection().rollback()

    ###################################################################
    # Utility Methods
    ###################################################################
    def check_db_connection(self) -> None:
        """
        Check connection and raise sqlite3.OperationalError if not connected.
        """
        if not self.is_connected():
            raise sqlite3.OperationalError("Database is not connected. Call connect() first.")

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        :param table_name: Name of the table to check.
        :return: True if table exists, False otherwise.
        """
        sql = """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name=?
        """
        result = self.fetch_one(sql=sql, params=(table_name,))
        return result is not None

    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """
        Get column information for a table.

        :param table_name: Name of the table.
        :return: List of column information rows.
        """
        self.check_db_connection()
        sql = f"PRAGMA table_info({table_name})"
        return self.fetch_all(sql=sql)
