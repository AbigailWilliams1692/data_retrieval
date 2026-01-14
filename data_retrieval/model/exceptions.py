#######################################################################
# Exception Classes
#######################################################################
class DataProviderError(Exception):
    """Base exception for data provider errors."""

    pass


class ConnectionError(DataProviderError):
    """Raised when connection to data source fails."""

    pass


class QueryError(DataProviderError):
    """Raised when a query operation fails."""

    pass


class ValidationError(DataProviderError):
    """Raised when data validation fails."""

    pass