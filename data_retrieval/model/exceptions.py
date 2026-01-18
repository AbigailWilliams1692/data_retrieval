#######################################################################
# Project: Data Retrieval Module
# File: exceptions.py
# Description: Exception classes for data providers
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-18
#######################################################################

#######################################################################
# Exception Classes
#######################################################################
class DataProviderError(Exception):
    """Base exception for data provider errors."""

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