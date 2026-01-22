#######################################################################
# Project: Data Retrieval Module
# File: __init__.py
# Description: Data Retrieval Module package initialization
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-18
#######################################################################

#######################################################################
# Import Core Classes
#######################################################################
from data_retrieval.model.data_provider import DataProvider
from data_retrieval.model.data_module import DataModule
from data_retrieval.model.exceptions import (
    DataProviderError,
    DataProviderConnectionError,
    DataFetchError,
    DataMethodNotFoundError,
    ReturnDataTypeNotMatchedError,
    ValidationError
)

#######################################################################
# Import Data Provider Implementations
#######################################################################
# REST API providers
from data_retrieval.data_provider.rest_api import RestAPI_DataProvider

# Database providers
from data_retrieval.data_provider.database import Database_DataProvider

#######################################################################
# Public API
#######################################################################
__all__ = [
    # Core classes
    "DataProvider",
    "DataModule",
    
    # Exceptions
    "DataProviderError",
    "DataProviderConnectionError",
    "DataFetchError",
    "DataMethodNotFoundError",
    "ReturnDataTypeNotMatchedError",
    "ValidationError",
    
    # REST API providers
    "RestAPI_DataProvider",
    
    # Database providers
    "Database_DataProvider",
]

#######################################################################
# Version Information
#######################################################################
__version__ = "1.0.0"
__author__ = "AbigailWilliams1692"
__email__ = "abigail.williams@example.com"
