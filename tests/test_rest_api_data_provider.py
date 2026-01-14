#!/usr/bin/env python3
"""
Unit tests for REST API data providers.

Author: AbigailWilliams1692
Created: 2026-01-14
"""

import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
import unittest
import requests
import aiohttp

from data_retrieval.data_provider.rest_api import RestAPI_DataProvider, RestAPI_AsyncDataProvider
from data_retrieval.model.query_result import QueryResult
from data_retrieval.model.exceptions import ConnectionError, QueryError


class TestRestDataProvider(unittest.TestCase):
    """Test cases for RestDataProvider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://api.example.com"
        self.headers = {"Authorization": "Bearer token"}
        self.provider = RestAPI_DataProvider(
            base_url=self.base_url,
            headers=self.headers,
            timeout=10.0
        )
    
    def test_initialization(self):
        """Test provider initialization."""
        self.assertEqual(self.provider._base_url, self.base_url)
        self.assertEqual(self.provider._default_headers, self.headers)
        self.assertEqual(self.provider._timeout, 10.0)
        self.assertIsNone(self.provider._session)
    
    def test_connect_success(self):
        """Test successful connection."""
        with patch('requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            
            self.provider._connect()
            
            self.assertIsNotNone(self.provider._session)
            mock_session.headers.update.assert_called_with(self.headers)
            mock_session.get.assert_called_with(
                f"{self.base_url}/health",
                timeout=10.0
            )
    
    def test_connect_failure(self):
        """Test connection failure."""
        with patch('requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            with self.assertRaises(ConnectionError):
                self.provider._connect()
    
    def test_disconnect(self):
        """Test disconnection."""
        mock_session = MagicMock()
        self.provider._session = mock_session
        
        self.provider._disconnect()
        
        mock_session.close.assert_called_once()
        self.assertIsNone(self.provider._session)
    
    def test_fetch_get_request(self):
        """Test GET request fetching."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"id": 1, "name": "Test User"},
            {"id": 2, "name": "Another User"}
        ]
        mock_response.headers = {"content-type": "application/json"}
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_session.request.return_value = mock_response
        self.provider._session = mock_session
        
        result = self.provider.fetch(endpoint="/users", params={"page": 1})
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]["name"], "Test User")
        self.assertEqual(result.total_count, 2)
        
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        self.assertEqual(call_args[0][0], "GET")
        self.assertIn("api.example.com/users", call_args[1]["url"])
    
    def test_fetch_post_request(self):
        """Test POST request fetching."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": 3, "name": "New User"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.elapsed.total_seconds.return_value = 0.3
        mock_session.request.return_value = mock_response
        self.provider._session = mock_session
        
        new_user = {"name": "New User", "email": "new@example.com"}
        result = self.provider.fetch(
            endpoint="/users",
            method="POST",
            data=new_user
        )
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["name"], "New User")
        
        call_args = mock_session.request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertEqual(call_args[1]["json"], new_user)
    
    def test_parse_response_json_list(self):
        """Test parsing JSON list response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
        
        data = self.provider._parse_response(mock_response)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "User 1")
    
    def test_parse_response_json_dict_with_results(self):
        """Test parsing JSON dict with results field."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "results": [{"id": 1, "name": "User 1"}],
            "total": 1
        }
        
        data = self.provider._parse_response(mock_response)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "User 1")
    
    def test_parse_response_json_single_object(self):
        """Test parsing JSON single object response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1, "name": "Single User"}
        
        data = self.provider._parse_response(mock_response)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Single User")
    
    def test_parse_response_non_json(self):
        """Test parsing non-JSON response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        
        data = self.provider._parse_response(mock_response)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], "Plain text response")
    
    def test_extract_pagination_info(self):
        """Test extracting pagination information."""
        mock_response = MagicMock()
        mock_response.headers = {
            "content-type": "application/json",
            "x-total-count": "100"
        }
        mock_response.json.return_value = {
            "results": [{"id": 1}],
            "total": 50,
            "count": 50,  # Add count field to avoid KeyError
            "page": 1,
            "page_size": 10
        }
        mock_response.status_code = 200
        mock_response.url = "http://example.com/api/users"
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        total_count, metadata = self.provider._extract_pagination_info(mock_response)
        
        self.assertEqual(total_count, 50)
        self.assertEqual(metadata["total"], 50)
        self.assertEqual(metadata["page"], 1)
        self.assertEqual(metadata["page_size"], 10)
        self.assertEqual(metadata["status_code"], 200)
    
    def test_health_check_success(self):
        """Test successful health check."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        self.provider._session = mock_session
        
        result = self.provider.health_check()
        
        self.assertTrue(result)
        mock_session.get.assert_called_with(
            f"{self.base_url}/health",
            timeout=5.0
        )
    
    def test_health_check_failure(self):
        """Test health check failure."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError()
        self.provider._session = mock_session
        
        result = self.provider.health_check()
        
        self.assertFalse(result)
    
    def test_fetch_without_connection(self):
        """Test fetching without established connection."""
        self.provider._session = None
        
        with self.assertRaises(ConnectionError):
            self.provider.fetch(endpoint="/users")
    
    def test_fetch_with_request_exception(self):
        """Test fetching with request exception."""
        mock_session = MagicMock()
        mock_session.request.side_effect = requests.exceptions.RequestException("Request failed")
        self.provider._session = mock_session
        
        with self.assertRaises(QueryError):
            self.provider.fetch(endpoint="/users")


class TestRestAPI_AsyncDataProvider(unittest.IsolatedAsyncioTestCase):
    """Test cases for RestAPI_AsyncDataProvider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://api.example.com"
        self.headers = {"Authorization": "Bearer token"}
        self.provider = RestAPI_AsyncDataProvider(
            base_url=self.base_url,
            headers=self.headers,
            timeout=10.0
        )
    
    def test_initialization(self):
        """Test async provider initialization."""
        self.assertEqual(self.provider._base_url, self.base_url)
        self.assertEqual(self.provider._default_headers, self.headers)
        self.assertEqual(self.provider._timeout, 10.0)
        self.assertIsNone(self.provider._session)
    
    async def test_connect_success(self):
        """Test successful async connection."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session.get.return_value.__aexit__.return_value = None
            
            await self.provider._connect()
            
            self.assertIsNotNone(self.provider._session)
            mock_session_class.assert_called_once()
    
    async def test_connect_failure(self):
        """Test async connection failure."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
            
            with self.assertRaises(ConnectionError):
                await self.provider._connect()
    
    async def test_disconnect(self):
        """Test async disconnection."""
        mock_session = AsyncMock()
        self.provider._session = mock_session
        
        await self.provider._disconnect()
        
        mock_session.close.assert_called_once()
        self.assertIsNone(self.provider._session)
    
    async def test_fetch_get_request(self):
        """Test async GET request fetching."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"id": 1, "name": "Test User"},
            {"id": 2, "name": "Another User"}
        ]
        mock_response.headers = {"content-type": "application/json"}
        mock_session.request.return_value.__aenter__.return_value = mock_response
        mock_session.request.return_value.__aexit__.return_value = None
        self.provider._session = mock_session
        
        result = await self.provider.fetch(endpoint="/users", params={"page": 1})
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]["name"], "Test User")
        
        mock_session.request.assert_called_once()
    
    async def test_fetch_post_request(self):
        """Test async POST request fetching."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": 3, "name": "New User"}
        mock_response.headers = {"content-type": "application/json"}
        mock_session.request.return_value.__aenter__.return_value = mock_response
        mock_session.request.return_value.__aexit__.return_value = None
        self.provider._session = mock_session
        
        new_user = {"name": "New User", "email": "new@example.com"}
        result = await self.provider.fetch(
            endpoint="/users",
            method="POST",
            data=new_user
        )
        
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["name"], "New User")
    
    async def test_parse_async_response_json_list(self):
        """Test parsing async JSON list response."""
        mock_response = AsyncMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
        
        data = await self.provider._parse_async_response(mock_response)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "User 1")
    
    async def test_extract_async_pagination_info(self):
        """Test extracting async pagination information."""
        mock_response = AsyncMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "results": [{"id": 1}],
            "total": 50,
            "count": 50,  # Add count field to avoid KeyError
            "page": 1
        }
        mock_response.status = 200
        mock_response.url = "http://example.com/api/users"
        
        total_count, metadata = await self.provider._extract_async_pagination_info(mock_response)
        
        self.assertEqual(total_count, 50)
        self.assertEqual(metadata["total"], 50)
        self.assertEqual(metadata["count"], 50)
        self.assertEqual(metadata["page"], 1)
        self.assertEqual(metadata["status_code"], 200)
    
    async def test_health_check_success(self):
        """Test successful async health check."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.get.return_value.__aexit__.return_value = None
        self.provider._session = mock_session
        
        result = await self.provider.health_check()
        
        self.assertTrue(result)
    
    async def test_health_check_failure(self):
        """Test async health check failure."""
        mock_session = AsyncMock()
        mock_session.get.side_effect = aiohttp.ClientError()
        self.provider._session = mock_session
        
        result = await self.provider.health_check()
        
        self.assertFalse(result)
    
    async def test_fetch_multiple_endpoints(self):
        """Test fetching from multiple endpoints concurrently."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{"id": 1}]
        mock_response.headers = {"content-type": "application/json"}
        mock_session.request.return_value.__aenter__.return_value = mock_response
        self.provider._session = mock_session
        
        endpoints = ["/users", "/posts", "/comments"]
        results = await self.provider.fetch_multiple(endpoints)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, QueryResult)
    
    async def test_fetch_multiple_with_exception(self):
        """Test fetching multiple endpoints with one failing."""
        mock_session = AsyncMock()
        mock_session.request.side_effect = [
            AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=[{"id": 1}]),
                headers={"content-type": "application/json"}
            ))),
            aiohttp.ClientError("Request failed"),
            AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(
                raise_for_status=AsyncMock(),
                json=AsyncMock(return_value=[{"id": 2}]),
                headers={"content-type": "application/json"}
            )))
        ]
        self.provider._session = mock_session
        
        endpoints = ["/users", "/posts", "/comments"]
        results = await self.provider.fetch_multiple(endpoints)
        
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], QueryResult)
        self.assertIsInstance(results[1], QueryResult)
        self.assertIsInstance(results[2], QueryResult)
        
        # Check that failed request has error metadata
        self.assertIn('error', results[1].metadata)
        self.assertEqual(results[1].metadata['endpoint'], '/posts')


if __name__ == '__main__':
    unittest.main()
