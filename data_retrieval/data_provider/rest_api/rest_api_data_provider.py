#######################################################################
# Project: Data Retrieval Module
# File: rest_api_provider.py
# Description: REST API data provider implementations
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlencode

# Third-party Packages
import requests
from requests import Response, Session
import aiohttp
import asyncio

# Local Packages
from data_retrieval.model.data_provider import DataProvider, AsyncDataProvider
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import ConnectionError, QueryError, ValidationError


#######################################################################
# REST API Data Provider (Synchronous)
#######################################################################
class RestAPI_DataProvider(DataProvider[Any]):
    """
    Synchronous REST API data provider.
    
    Provides standardized interface for interacting with REST APIs.
    Supports authentication, pagination, error handling, and retry logic.
    
    Example Usage:
        provider = RestDataProvider(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"}
        )
        
        with provider.connection():
            result = provider.fetch(endpoint="/users", params={"page": 1})
            for user in result.data:
                print(user)
    """
    
    #################################################
    # Class Attributes
    #################################################
    __name = "RestAPI_DataProvider"
    __type = "RestAPI_DataProvider"
    __base_url: str = ""
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
        verify_ssl: bool = True,
        **kwargs
    ):
        """
        Initialize REST API provider.
        
        :param base_url: Base URL for the API
        :param headers: Default headers for requests
        :param timeout: Request timeout in seconds
        :param verify_ssl: Whether to verify SSL certificates
        """
        super().__init__(**kwargs)
        self._default_headers = headers or {}
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._session: Optional[Session] = None
        self._connection_config = {}
    
    def _connect(self) -> None:
        """
        Establish HTTP session.
        """
        self._session = Session()
        self._session.headers.update(self._default_headers)
        self._session.verify = self._verify_ssl
        
        # Test connection
        try:
            response = self._session.get(
                f"{self.__base_url}/health",
                timeout=self._timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to API: {e}") from e
    
    def _disconnect(self) -> None:
        """
        Close HTTP session.
        """
        if self._session:
            self._session.close()
            self._session = None
    
    def fetch(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        data: Optional[Union[Dict, str]] = None,
        **kwargs
    ) -> QueryResult[Any]:
        """
        Fetch data from REST API.
        
        :param endpoint: API endpoint (relative to base_url)
        :param params: Query parameters
        :param headers: Additional headers for this request
        :param method: HTTP method (GET, POST, PUT, DELETE)
        :param data: Request body data
        :return: QueryResult containing fetched data
        """
        if not self._session:
            raise ConnectionError("Not connected to API")
        
        # Build URL
        url = urljoin(self.__base_url + "/", endpoint.lstrip("/"))
        
        # Merge headers
        request_headers = self._default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare request arguments
        request_kwargs = {
            "headers": request_headers,
            "timeout": self._timeout,
            "params": params,
            **kwargs
        }
        
        # Add request body for methods that support it
        if method.upper() in ["POST", "PUT", "PATCH"] and data:
            if isinstance(data, dict):
                request_kwargs["json"] = data
            else:
                request_kwargs["data"] = data
        
        try:
            # Make request
            response = self._session.request(method, url, **request_kwargs)
            response.raise_for_status()
            
            # Parse response
            response_data = self._parse_response(response)
            
            # Handle pagination
            total_count, metadata = self._extract_pagination_info(response)
            
            # Validate and transform data
            validated_data = []
            for item in response_data:
                if self.validate(item):
                    transformed_item = self.transform(item)
                    validated_data.append(transformed_item)
                else:
                    self.get_logger().warning(f"Invalid data item: {item}")
            
            return QueryResult(
                data=validated_data,
                total_count=total_count,
                metadata=metadata
            )
            
        except requests.exceptions.RequestException as e:
            raise QueryError(f"API request failed: {e}") from e
    
    def _parse_response(self, response: Response) -> List[Any]:
        """Parse API response and extract data."""
        content_type = response.headers.get("content-type", "").lower()
        
        if "application/json" in content_type:
            data = response.json()
            # Handle different response structures
            if isinstance(data, dict):
                # Common patterns: data.results, data.items, data.data
                for key in ["results", "items", "data", "content"]:
                    if key in data:
                        return data[key]
                # If it"s a single object, wrap in list
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            # Non-JSON response
            return [response.text]
    
    def _extract_pagination_info(self, response: Response) -> tuple[int, Dict[str, Any]]:
        """Extract pagination information from response."""
        metadata = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "url": response.url,
            "request_time": response.elapsed.total_seconds()
        }
        
        total_count = 0
        
        # Try to extract total count from response
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Common pagination fields
                    for key in ["total", "count", "total_items", "totalCount"]:
                        if key in data:
                            total_count = int(data[key])
                            break
                    
                    # Add pagination metadata
                    pagination_fields = ["page", "page_size", "pages", "next", "previous", "has_next", "has_previous", "total", "count", "total_items", "totalCount"]
                    pagination_meta = {k: v for k, v in data.items() if k in pagination_fields}
                    metadata.update(pagination_meta)
            except (ValueError, KeyError):
                pass
        
        return total_count, metadata
    
    def health_check(self) -> bool:
        """Check API health status."""
        try:
            if not self._session:
                return False
            
            response = self._session.get(
                f"{self.__base_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False


#######################################################################
# Async REST API Data Provider
#######################################################################
class RestAPI_AsyncDataProvider(AsyncDataProvider[Any]):
    """
    Asynchronous REST API data provider.
    
    Provides async interface for interacting with REST APIs.
    Supports concurrent requests and efficient resource management.
    
    Example Usage:
        async def fetch_users():
            provider = AsyncRestDataProvider(
                base_url="https://api.example.com",
                headers={"Authorization": "Bearer token"}
            )
            
            async with provider.async_connection():
                result = await provider.fetch(endpoint="/users")
                return result.data
    """
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        connector_limit: int = 100,
        **kwargs
    ):
        """
        Initialize async REST API provider.
        
        :param base_url: Base URL for the API
        :param headers: Default headers for requests
        :param timeout: Request timeout in seconds
        :param verify_ssl: Whether to verify SSL certificates
        :param connector_limit: Maximum number of concurrent connections
        """
        super().__init__(**kwargs)
        self.__base_url = base_url.rstrip("/")
        self._default_headers = headers or {}
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._connector_limit = connector_limit
        self._session: Optional[aiohttp.ClientSession] = None
        self._connection_config = {}
    
    async def _connect(self) -> None:
        """Establish async HTTP session."""
        connector = aiohttp.TCPConnector(
            limit=self._connector_limit,
            verify_ssl=self._verify_ssl
        )
        
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._default_headers
        )
        
        # Test connection
        try:
            async with self._session.get(f"{self.__base_url}/health") as response:
                response.raise_for_status()
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to connect to API: {e}") from e
    
    async def _disconnect(self) -> None:
        """
        Close async HTTP session.
        """
        if self._session:
            await self._session.close()
            self._session = None
    
    async def fetch(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        data: Optional[Union[Dict, str]] = None,
        **kwargs
    ) -> QueryResult[Any]:
        """
        Fetch data from REST API asynchronously.
        
        :param endpoint: API endpoint (relative to base_url)
        :param params: Query parameters
        :param headers: Additional headers for this request
        :param method: HTTP method (GET, POST, PUT, DELETE)
        :param data: Request body data
        :return: QueryResult containing fetched data
        """
        if not self._session:
            raise ConnectionError("Not connected to API")
        
        # Build URL
        url = urljoin(self.__base_url + "/", endpoint.lstrip("/"))
        
        # Merge headers
        request_headers = self._default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            # Make async request
            async with self._session.request(
                method,
                url,
                params=params,
                headers=request_headers,
                json=data if isinstance(data, dict) and method.upper() in ["POST", "PUT", "PATCH"] else None,
                data=data if not isinstance(data, dict) else None,
                **kwargs
            ) as response:
                response.raise_for_status()
                
                # Parse response
                response_data = await self._parse_async_response(response)
                
                # Handle pagination
                total_count, metadata = await self._extract_async_pagination_info(response)
                
                # Validate and transform data
                validated_data = []
                for item in response_data:
                    if await self.validate(item):
                        transformed_item = await self.transform(item)
                        validated_data.append(transformed_item)
                    else:
                        self.get_logger().warning(f"Invalid data item: {item}")
                
                return QueryResult(
                    data=validated_data,
                    total_count=total_count,
                    metadata=metadata
                )
                
        except aiohttp.ClientError as e:
            raise QueryError(f"API request failed: {e}") from e
    
    async def _parse_async_response(self, response: aiohttp.ClientResponse) -> List[Any]:
        """
        Parse async API response and extract data.
        """
        content_type = response.headers.get("content-type", "").lower()
        
        if "application/json" in content_type:
            data = await response.json()
            # Handle different response structures
            if isinstance(data, dict):
                # Common patterns: data.results, data.items, data.data
                for key in ["results", "items", "data", "content"]:
                    if key in data:
                        return data[key]
                # If it"s a single object, wrap in list
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            # Non-JSON response
            text = await response.text()
            return [text]
    
    async def _extract_async_pagination_info(self, response: aiohttp.ClientResponse) -> tuple[int, Dict[str, Any]]:
        """
        Extract pagination information from async response.
        """
        metadata = {
            "status_code": response.status,
            "headers": dict(response.headers),
            "url": str(response.url),
        }
        
        total_count = 0
        
        # Try to extract total count from response
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            try:
                data = await response.json()
                if isinstance(data, dict):
                    # Common pagination fields
                    for key in ["total", "count", "total_items", "totalCount"]:
                        if key in data:
                            total_count = int(data[key])
                            break
                    
                    # Add pagination metadata
                    pagination_fields = ["page", "page_size", "pages", "next", "previous", "has_next", "has_previous", "total", "count", "total_items", "totalCount"]
                    pagination_meta = {k: v for k, v in data.items() if k in pagination_fields}
                    metadata.update(pagination_meta)
            except (ValueError, KeyError):
                pass
        
        return total_count, metadata
    
    async def health_check(self) -> bool:
        """
        Check API health status asynchronously.
        """
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.__base_url}/health", timeout=5.0) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def fetch_multiple(
        self,
        endpoints: List[str],
        **common_kwargs
    ) -> List[QueryResult[Any]]:
        """
        Fetch data from multiple endpoints concurrently.
        
        :param endpoints: List of endpoints to fetch
        :param common_kwargs: Common arguments for all requests
        :return: List of QueryResult objects
        """
        if not self._session:
            raise ConnectionError("Not connected to API")
        
        tasks = []
        for endpoint in endpoints:
            task = self.fetch(endpoint=endpoint, **common_kwargs)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to QueryResult with error information
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.get_logger().error(f"Failed to fetch {endpoints[i]}: {result}")
                final_results.append(QueryResult(
                    data=[],
                    total_count=0,
                    metadata={"error": str(result), "endpoint": endpoints[i]}
                ))
            else:
                final_results.append(result)
        
        return final_results
