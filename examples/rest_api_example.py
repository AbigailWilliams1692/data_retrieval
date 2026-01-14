#!/usr/bin/env python3
"""
REST API Data Provider Example
Demonstrates how to use RestAPI_DataProvider and RestAPI_AsyncDataProvider

Author: AbigailWilliams1692
Created: 2026-01-14
"""

import asyncio
import json
from data_retrieval import RestAPI_DataProvider, RestAPI_AsyncDataProvider


def sync_rest_api_example():
    """Example of synchronous REST API usage."""
    print("=== Synchronous REST API Example ===")
    
    # Create provider
    provider = RestAPI_DataProvider(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"Content-Type": "application/json"},
        timeout=10.0
    )
    
    try:
        with provider.connection():
            # Fetch users
            print("Fetching users...")
            result = provider.fetch(endpoint="/users")
            
            print(f"Found {len(result.data)} users")
            print(f"Total count: {result.total_count}")
            
            # Display first user
            if result.data:
                first_user = result.data[0]
                print(f"First user: {first_user.get('name', 'Unknown')}")
                print(f"Email: {first_user.get('email', 'N/A')}")
            
            # Fetch posts for a specific user
            print("\nFetching posts for user 1...")
            posts_result = provider.fetch(
                endpoint="/posts",
                params={"userId": 1}
            )
            
            print(f"Found {len(posts_result.data)} posts for user 1")
            
            # Create a new post (POST request)
            print("\nCreating a new post...")
            new_post = {
                "title": "Test Post",
                "body": "This is a test post created via REST API provider",
                "userId": 1
            }
            
            create_result = provider.fetch(
                endpoint="/posts",
                method="POST",
                data=new_post
            )
            
            if create_result.data:
                created_post = create_result.data[0]
                print(f"Created post with ID: {created_post.get('id')}")
                print(f"Title: {created_post.get('title')}")
    
    except Exception as e:
        print(f"Error: {e}")


async def async_rest_api_example():
    """Example of asynchronous REST API usage."""
    print("\n=== Asynchronous REST API Example ===")
    
    # Create async provider
    provider = RestAPI_AsyncDataProvider(
        base_url="https://jsonplaceholder.typicode.com",
        headers={"Content-Type": "application/json"},
        timeout=10.0
    )
    
    try:
        async with provider.async_connection():
            # Fetch multiple endpoints concurrently
            print("Fetching data from multiple endpoints concurrently...")
            
            endpoints = ["/users", "/posts", "/comments"]
            results = await provider.fetch_multiple(endpoints)
            
            for i, (endpoint, result) in enumerate(zip(endpoints, results)):
                print(f"{endpoint}: {len(result.data)} items")
            
            # Fetch users with custom validation
            print("\nFetching users with validation...")
            
            # Override validate method to filter users
            original_validate = provider.validate
            
            def validate_user(user):
                # Only accept users with valid email
                email = user.get('email', '')
                return '@' in email and '.' in email.split('@')[-1]
            
            provider.validate = validate_user
            
            users_result = await provider.fetch(endpoint="/users")
            print(f"Valid users found: {len(users_result.data)}")
            
            # Restore original validation
            provider.validate = original_validate
    
    except Exception as e:
        print(f"Error: {e}")


def custom_rest_api_example():
    """Example with custom REST API configuration."""
    print("\n=== Custom REST API Example ===")
    
    # Provider with custom configuration
    provider = RestAPI_DataProvider(
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DataRetrievalModule/1.0.0"
        },
        timeout=15.0
    )
    
    try:
        with provider.connection():
            # Fetch GitHub repositories for a user
            print("Fetching GitHub repositories for 'octocat'...")
            result = provider.fetch(endpoint="/users/octocat/repos")
            
            print(f"Found {len(result.data)} repositories")
            
            # Display repository information
            if result.data:
                for repo in result.data[:3]:  # Show first 3
                    name = repo.get('name', 'Unknown')
                    stars = repo.get('stargazers_count', 0)
                    language = repo.get('language', 'Unknown')
                    print(f"- {name}: {stars} stars, {language}")
    
    except Exception as e:
        print(f"Error: {e}")


def error_handling_example():
    """Example of error handling with REST API provider."""
    print("\n=== Error Handling Example ===")
    
    provider = RestAPI_DataProvider(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=5.0
    )
    
    try:
        with provider.connection():
            # Try to fetch from non-existent endpoint
            print("Attempting to fetch from non-existent endpoint...")
            result = provider.fetch(endpoint="/nonexistent")
            
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")
    
    try:
        # Try to connect to invalid URL
        print("\nAttempting to connect to invalid URL...")
        invalid_provider = RestAPI_DataProvider(
            base_url="https://invalid-url-that-does-not-exist.com",
            timeout=5.0
        )
        
        with invalid_provider.connection():
            pass
            
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Run synchronous examples
    sync_rest_api_example()
    custom_rest_api_example()
    error_handling_example()
    
    # Run asynchronous example
    asyncio.run(async_rest_api_example())
    
    print("\n=== All Examples Completed ===")
