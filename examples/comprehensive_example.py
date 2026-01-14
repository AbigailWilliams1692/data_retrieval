#!/usr/bin/env python3
"""
Comprehensive Example
Demonstrates using all data providers together in a unified application

Author: AbigailWilliams1692
Created: 2026-01-14
"""

import asyncio
import json
from typing import Dict, Any, List

from data_retrieval import (
    RestAPI_DataProvider, RestAPI_AsyncDataProvider,
    Database_DataProvider, Database_AsyncDataProvider,
    DatabaseConfig, QueryResult
)


class UnifiedDataProcessor:
    """
    Example class that demonstrates using multiple data providers
    to create a unified data processing system.
    """
    
    def __init__(self):
        """Initialize the data processor with multiple providers."""
        # REST API provider for external data
        self.api_provider = RestAPI_DataProvider(
            base_url="https://jsonplaceholder.typicode.com",
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        # Database provider for local storage
        self.db_config = DatabaseConfig(
            database_type='sqlite',
            database='unified_example.db'
        )
        self.db_provider = Database_DataProvider(self.db_config)
        
        # Async providers for concurrent operations
        self.async_api_provider = RestAPI_AsyncDataProvider(
            base_url="https://jsonplaceholder.typicode.com",
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        self.async_db_provider = Database_AsyncDataProvider(self.db_config)
    
    def setup_database(self):
        """Set up the database schema."""
        print("Setting up database...")
        
        with self.db_provider.connection():
            # Create users table
            self.db_provider.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT,
                    phone TEXT,
                    website TEXT,
                    api_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create posts table
            self.db_provider.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    body TEXT,
                    api_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create comments table
            self.db_provider.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    post_id INTEGER,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    body TEXT,
                    api_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            ''')
            
            print("Database schema created successfully")
    
    def sync_data_from_api(self):
        """Synchronously fetch data from API and store in database."""
        print("\n=== Synchronous Data Sync ===")
        
        try:
            with self.api_provider.connection():
                # Fetch users from API
                print("Fetching users from API...")
                users_result = self.api_provider.fetch(endpoint="/users")
                print(f"Fetched {len(users_result.data)} users")
                
                # Store users in database
                with self.db_provider.connection():
                    users_stored = 0
                    for user in users_result.data:
                        try:
                            self.db_provider.execute('''
                                INSERT OR REPLACE INTO users 
                                (id, name, email, username, phone, website, api_source)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', params=[
                                user.get('id'),
                                user.get('name'),
                                user.get('email'),
                                user.get('username'),
                                user.get('phone'),
                                user.get('website'),
                                'jsonplaceholder'
                            ])
                            users_stored += 1
                        except Exception as e:
                            print(f"Error storing user {user.get('id')}: {e}")
                    
                    print(f"Stored {users_stored} users in database")
                    
                    # Fetch posts for each user
                    print("\nFetching posts from API...")
                    posts_result = self.api_provider.fetch(endpoint="/posts")
                    print(f"Fetched {len(posts_result.data)} posts")
                    
                    # Store posts in database
                    posts_stored = 0
                    for post in posts_result.data:
                        try:
                            self.db_provider.execute('''
                                INSERT OR REPLACE INTO posts 
                                (id, user_id, title, body, api_source)
                                VALUES (?, ?, ?, ?, ?)
                            ''', params=[
                                post.get('id'),
                                post.get('userId'),
                                post.get('title'),
                                post.get('body'),
                                'jsonplaceholder'
                            ])
                            posts_stored += 1
                        except Exception as e:
                            print(f"Error storing post {post.get('id')}: {e}")
                    
                    print(f"Stored {posts_stored} posts in database")
        
        except Exception as e:
            print(f"Error in sync data operation: {e}")
    
    async def async_data_from_api(self):
        """Asynchronously fetch data from API and store in database."""
        print("\n=== Asynchronous Data Sync ===")
        
        try:
            async with self.async_api_provider.async_connection():
                # Fetch multiple endpoints concurrently
                print("Fetching data from multiple API endpoints concurrently...")
                endpoints = ["/users", "/posts", "/comments"]
                results = await self.async_api_provider.fetch_multiple(endpoints)
                
                users_result, posts_result, comments_result = results
                
                print(f"Fetched {len(users_result.data)} users")
                print(f"Fetched {len(posts_result.data)} posts")
                print(f"Fetched {len(comments_result.data)} comments")
                
                # Store data in database asynchronously
                async with self.async_db_provider.async_connection():
                    # Store users
                    users_stored = 0
                    for user in users_result.data:
                        try:
                            await self.async_db_provider.execute('''
                                INSERT OR REPLACE INTO users 
                                (id, name, email, username, phone, website, api_source)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', params=[
                                user.get('id'),
                                user.get('name'),
                                user.get('email'),
                                user.get('username'),
                                user.get('phone'),
                                user.get('website'),
                                'jsonplaceholder_async'
                            ])
                            users_stored += 1
                        except Exception as e:
                            print(f"Error storing user {user.get('id')}: {e}")
                    
                    print(f"Stored {users_stored} users in database (async)")
                    
                    # Store posts
                    posts_stored = 0
                    for post in posts_result.data:
                        try:
                            await self.async_db_provider.execute('''
                                INSERT OR REPLACE INTO posts 
                                (id, user_id, title, body, api_source)
                                VALUES (?, ?, ?, ?, ?)
                            ''', params=[
                                post.get('id'),
                                post.get('userId'),
                                post.get('title'),
                                post.get('body'),
                                'jsonplaceholder_async'
                            ])
                            posts_stored += 1
                        except Exception as e:
                            print(f"Error storing post {post.get('id')}: {e}")
                    
                    print(f"Stored {posts_stored} posts in database (async)")
                    
                    # Store comments
                    comments_stored = 0
                    for comment in comments_result.data:
                        try:
                            await self.async_db_provider.execute('''
                                INSERT OR REPLACE INTO comments 
                                (id, post_id, name, email, body, api_source)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', params=[
                                comment.get('id'),
                                comment.get('postId'),
                                comment.get('name'),
                                comment.get('email'),
                                comment.get('body'),
                                'jsonplaceholder_async'
                            ])
                            comments_stored += 1
                        except Exception as e:
                            print(f"Error storing comment {comment.get('id')}: {e}")
                    
                    print(f"Stored {comments_stored} comments in database (async)")
        
        except Exception as e:
            print(f"Error in async data operation: {e}")
    
    def analyze_data(self):
        """Analyze the stored data and generate insights."""
        print("\n=== Data Analysis ===")
        
        try:
            with self.db_provider.connection():
                # User statistics
                users_count = self.db_provider.fetch("SELECT COUNT(*) as count FROM users")
                print(f"Total users: {users_count.data[0]['count']}")
                
                # Posts per user
                posts_per_user = self.db_provider.fetch('''
                    SELECT u.name, COUNT(p.id) as post_count
                    FROM users u
                    LEFT JOIN posts p ON u.id = p.user_id
                    GROUP BY u.id, u.name
                    ORDER BY post_count DESC
                    LIMIT 5
                ''')
                
                print("\nTop 5 users by post count:")
                for row in posts_per_user.data:
                    print(f"  - {row['name']}: {row['post_count']} posts")
                
                # API source distribution
                api_sources = self.db_provider.fetch('''
                    SELECT api_source, COUNT(*) as count
                    FROM users
                    GROUP BY api_source
                ''')
                
                print("\nUsers by API source:")
                for row in api_sources.data:
                    print(f"  - {row['api_source']}: {row['count']} users")
                
                # Recent activity
                recent_posts = self.db_provider.fetch('''
                    SELECT p.title, u.name, p.created_at
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    ORDER BY p.created_at DESC
                    LIMIT 3
                ''')
                
                print("\nRecent posts:")
                for post in recent_posts.data:
                    print(f"  - {post['title']} by {post['name']}")
        
        except Exception as e:
            print(f"Error in data analysis: {e}")
    
    def demonstrate_validation_and_transformation(self):
        """Demonstrate custom validation and transformation."""
        print("\n=== Validation and Transformation Demo ===")
        
        # Custom validation for API provider
        original_validate = self.api_provider.validate
        
        def validate_user_data(user_data):
            """Custom validation for user data."""
            required_fields = ['id', 'name', 'email']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return False
            
            # Validate email format
            email = user_data.get('email', '')
            if '@' not in email or '.' not in email.split('@')[1]:
                return False
            
            return True
        
        # Custom transformation
        def transform_user_data(user_data):
            """Custom transformation for user data."""
            transformed = user_data.copy()
            
            # Add computed fields
            transformed['domain'] = user_data.get('email', '').split('@')[1] if '@' in user_data.get('email', '') else ''
            transformed['name_length'] = len(user_data.get('name', ''))
            
            # Clean up data
            if 'phone' in transformed and not transformed['phone']:
                del transformed['phone']
            
            return transformed
        
        # Apply custom validation and transformation
        self.api_provider.validate = validate_user_data
        self.api_provider.transform = transform_user_data
        
        try:
            with self.api_provider.connection():
                print("Fetching users with custom validation and transformation...")
                result = self.api_provider.fetch(endpoint="/users")
                
                print(f"Validated and transformed {len(result.data)} users")
                
                # Show transformed data
                if result.data:
                    sample_user = result.data[0]
                    print(f"Sample transformed user:")
                    print(f"  - Name: {sample_user.get('name')}")
                    print(f"  - Domain: {sample_user.get('domain')}")
                    print(f"  - Name length: {sample_user.get('name_length')}")
        
        except Exception as e:
            print(f"Error in validation/transformation demo: {e}")
        
        # Restore original validation
        self.api_provider.validate = original_validate
    
    def demonstrate_error_handling(self):
        """Demonstrate error handling capabilities."""
        print("\n=== Error Handling Demo ===")
        
        # Test API error handling
        try:
            invalid_provider = RestAPI_DataProvider(
                base_url="https://invalid-url.example.com",
                timeout=5.0
            )
            
            with invalid_provider.connection():
                pass  # This should fail
                
        except Exception as e:
            print(f"API connection error handled: {type(e).__name__}: {e}")
        
        # Test database error handling
        try:
            with self.db_provider.connection():
                # This should cause an SQL error
                self.db_provider.fetch("SELECT * FROM nonexistent_table")
                
        except Exception as e:
            print(f"Database query error handled: {type(e).__name__}: {e}")
        
        # Test retry logic
        try:
            with self.api_provider.connection():
                # Simulate a failing operation
                def failing_operation():
                    raise Exception("Simulated failure")
                
                result = self.api_provider.with_retry(
                    failing_operation,
                    max_retries=2,
                    retry_delay=0.1,
                    parameters={}
                )
                
        except Exception as e:
            print(f"Retry logic error handled: {type(e).__name__}: {e}")
    
    def run_comprehensive_demo(self):
        """Run the complete comprehensive demonstration."""
        print("🚀 Starting Comprehensive Data Provider Demo")
        print("=" * 60)
        
        # Setup
        self.setup_database()
        
        # Synchronous operations
        self.sync_data_from_api()
        
        # Asynchronous operations
        asyncio.run(self.async_data_from_api())
        
        # Data analysis
        self.analyze_data()
        
        # Validation and transformation
        self.demonstrate_validation_and_transformation()
        
        # Error handling
        self.demonstrate_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ Comprehensive Demo Completed Successfully!")


def main():
    """Main function to run the comprehensive example."""
    processor = UnifiedDataProcessor()
    processor.run_comprehensive_demo()


if __name__ == "__main__":
    main()
