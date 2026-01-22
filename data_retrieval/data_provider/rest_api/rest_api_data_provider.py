#######################################################################
# Project: Data Retrieval Module
# File: rest_api_provider.py
# Description: REST API data provider implementations
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-19
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from abc import ABC
from collections.abc import Generator
from typing import Any, Dict, List, Optional

# Third-party Packages
import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util import Retry

# Local Packages
from data_retrieval.model.data_provider import DataProvider


#######################################################################
# REST API Data Provider (Synchronous)
#######################################################################
class RestAPI_DataProvider(DataProvider, ABC):
    """
    Synchronous REST API data provider.
    
    Provides standardized interface for interacting with REST APIs.
    Supports authentication, pagination, error handling, and retry logic.
    """
    
    ###################################################################
    # Class Attributes
    ###################################################################
    __name = "RestAPI_DataProvider"
    __type = "RestAPI_DataProvider"
    __base_url: str = ""
    
    ###################################################################
    # Constructor Method
    ###################################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.3,
        **config
    ) -> None:
        """
        Initialize the REST API data provider.
        
        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the data provider.
        :param data_methods: Dictionary of data retrieval methods.
        :param base_url: Base URL for the REST API.
        :param timeout: Request timeout in seconds.
        :param max_retries: Maximum number of retry attempts.
        :param retry_backoff_factor: Backoff factor for retry delays.
        :param config: Additional configuration parameters.
        """
        # Initialize the base DataProvider
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            **config
        )

        # Prepare the data methods
        self.update_data_methods(
            {
                "http_request": self._make_request,
            }
        )
        
        # Initialize REST API specific attributes
        self._base_url = base_url or self.__base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_backoff_factor = retry_backoff_factor
        
        # Connect to the Session
        self.connect()

        # Initialize session with retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.get_connection().mount("http://", adapter)
        self.get_connection().mount("https://", adapter)

    ###################################################################
    # Getter & Setter Methods
    ###################################################################
    def get_base_url(self) -> str:
        """
        Get the base URL of the API server.

        :return: The base URL of the API server.
        """
        return self.__base_url
    
    def set_base_url(self, base_url: str) -> None:
        """
        Set the base URL of the API server.
        
        :param base_url: The base URL of the API server.
        """
        self.__base_url = base_url.rstrip("/")

    ###################################################################
    # Core Instance Method: Make Request to REST API Server
    ###################################################################
    def _make_request(
        self,
        url: str,
        method: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        authentication: Optional[Any] = None,
    ) -> Dict:
        """
        Make HTTP request to REST API endpoint.
        
        :param url: Endpoint URL (relative to base_url)
        :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
        :param params: Query parameters
        :param data: Form data to send
        :param json: JSON data to send
        :param headers: Additional headers
        :param authentication: Override default authentication
        
        :return: Response data as dictionary.
        :raises: HTTPError if request fails.
        """
        # Logging the Request
        self.get_logger().debug(f"Making {method.upper()} request to {url}")

        # Make the request
        try:
            response: Response = self.get_connection().request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                auth=authentication,
            )

            ## Raise an error for bad response (4xx and 5xx)
            response.raise_for_status()

            ## If the response is successful, return the JSON content
            self.get_logger().debug(f"Request succeeded: {response.status_code}.")
            return response.json()

        except requests.exceptions.RequestException as e:
            self.get_logger().error(f"Request failed: {e}")
            return {}

    ###################################################################
    # Core Instance Method: Fetch Data
    ##################################################################
    def fetch_data(self, data_point: str, return_data_type: type, *args, **kwargs) -> Any:
        """
        Base method to fetch data based on the data point and return type.

        :param data_point: str: The data point to fetch.
        :param return_data_type: type: The type of data to return.
        :param args: Tuple: Positional arguments for fetching data.
        :param kwargs: Dict: Keyword arguments for fetching data.
        :return: The fetched data.
        """
        return super().fetch_data(data_point=data_point, return_data_type=return_data_type, *args, **kwargs)

    ###################################################################
    # Connection Methods
    ###################################################################
    def _connect(self) -> None:
        """
        Connect to Aladdin API server.
        """
        self.set_connection(connection=requests.Session())

    def _disconnect(self, *args, **kwargs):
        if self.get_connection() is not None:
            self.get_connection().close()
            self.set_connection(connection=None)

    ###################################################################
    # Utility Methods
    ###################################################################
    @staticmethod
    def generate_headers(*args, **kwargs) -> Dict:
        """
        Generate default HTTP headers for API requests.
        
        :param args: Additional positional arguments (unused).
        :param kwargs: Additional keyword arguments (unused).
        :return: Dictionary containing default HTTP headers.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
        }
        return headers
    
    def generate_authentication(self, authentication_type: str, *args, **kwargs) -> Any:
        """
        Generate the authentication for the request.

        :param args: Additional positional arguments (unused).
        :param kwargs: Additional keyword arguments (unused).
        :return: the Authentication.
        """
        if authentication_type == "HTTPBasicAuth":
            return self.generate_http_authentication(*args, **kwargs)
        else:
            return None

    @staticmethod
    def generate_http_authentication(username: str, password: str) -> Any:
        """
        Generate HTTP authentication for the request.
        
        :param username: The username for authentication.
        :param password: The password for authentication.
        :return: The HTTP authentication.
        """
        return HTTPBasicAuth(username=username, password=password)
    
    @staticmethod
    def partition_list_into_chunks(item_list: List[Any], chunk_length: int = 100) -> Generator[List[Any], None, None]:
        """
        Return a generator that yields successive n-size chunks of list of items.

        :param item_list: a list of items.
        :param chunk_length: the length of each chunk.
        """
        for i in range(0, len(item_list), chunk_length):
            yield item_list[i:i + chunk_length]
