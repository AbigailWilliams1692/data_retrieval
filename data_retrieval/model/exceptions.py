#######################################################################
# Project: Data Retrieval Module
# File: exceptions.py
# Description: Exception classes for data providers
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-24
#######################################################################

#######################################################################
# Data Provider Exceptions
#######################################################################
class DataProviderError(Exception):
    """Base exception for data provider errors."""
    pass


class DataProviderInitializationError(DataProviderError):
    """Raised when initialization of data provider fails."""
    pass


class DataProviderConnectionError(DataProviderError):
    """Raised when connection to data source fails."""
    pass


class DataFetchError(DataProviderError):
    """Raised when a query operation fails."""
    pass

class DataMethodNotFoundError(DataProviderError):
    """Raised when a requested data method is not found."""
    pass

class ReturnDataTypeNotMatchedError(DataProviderError):
    """Raised when the retrieved data type does not match the expected type."""
    pass


class ValidationError(DataProviderError):
    """Raised when data validation fails."""
    pass


#######################################################################
# Data Provider Wrapper Exceptions
#######################################################################
class DataProviderWrapperError(Exception):
    """Base exception for data provider wrapper errors."""
    pass

class DataProviderNotFoundError(DataProviderWrapperError):
    """Raised when cannot find the corresponding data provider class."""
    pass

class DataProviderWrapperConnectionError(DataProviderWrapperError):
    """Raised when connection to data provider fails."""
    pass