#######################################################################
# Project: Data Retrieval Module
# File: query_result.py
# Description: Standardized query result container
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2025-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
from dataclasses import dataclass, field
from typing import Generic, TypeVar, List, Dict, Any


#######################################################################
# Constants
#######################################################################
T = TypeVar("T")


#######################################################################
# Class Definition
#######################################################################
@dataclass
class QueryResult(Generic[T]):
    """
    Standardized query result container.

    :param data: List of retrieved items.
    :param total_count: Total number of items matching the query (for pagination).
    :param page: Current page number (1-indexed).
    :param page_size: Number of items per page.
    :param has_more: Indicates if more pages are available.
    :param metadata: Additional metadata from the data source.
    """

    data: List[T] = field(default_factory=list)
    total_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """
        Check if the result is empty.
        """
        return self.total_count == 0
        