#!/usr/bin/env python3
"""
Database Data Provider Example
Demonstrates how to use DatabaseProvider and AsyncDatabaseProvider

Author: AbigailWilliams1692
Created: 2026-01-14
"""

import asyncio
import sqlite3
from data_retrieval import Database_DataProvider, Database_AsyncDataProvider, DatabaseConfig


def create_sample_sqlite_db():
    """Create a sample SQLite database for demonstration."""
    conn = sqlite3.connect('sample.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Insert sample data
    users = [
        ('Alice Johnson', 'alice@example.com', 28, True),
        ('Bob Smith', 'bob@example.com', 35, True),
        ('Charlie Brown', 'charlie@example.com', 42, False),
        ('Diana Prince', 'diana@example.com', 30, True),
        ('Eve Wilson', 'eve@example.com', 25, True)
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO users (name, email, age, active) VALUES (?, ?, ?, ?)',
        users
    )
    
    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample posts
    posts = [
        (1, 'First Post', 'This is my first post'),
        (1, 'Second Post', 'Another post from Alice'),
        (2, 'Hello World', 'Bob is saying hello'),
        (3, 'Random Thoughts', 'Charlie\'s random thoughts'),
        (4, 'Tech Talk', 'Diana talks about technology'),
        (5, 'Daily Life', 'Eve shares her daily experiences')
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO posts (user_id, title, content) VALUES (?, ?, ?)',
        posts
    )
    
    conn.commit()
    conn.close()
    print("Sample SQLite database created: sample.db")


def sync_database_example():
    """Example of synchronous database usage."""
    print("=== Synchronous Database Example ===")
    
    # Create sample database
    create_sample_sqlite_db()
    
    # Configure database connection
    config = DatabaseConfig(
        database_type='sqlite',
        database='sample.db'
    )
    
    # Create provider
    provider = Database_DataProvider(config)
    
    try:
        with provider.connection():
            # Fetch all users
            print("Fetching all users...")
            users_result = provider.fetch("SELECT * FROM users")
            
            print(f"Found {len(users_result.data)} users")
            for user in users_result.data:
                print(f"  - {user['name']} ({user['email']}) - Age: {user['age']}")
            
            # Fetch active users only
            print("\nFetching active users only...")
            active_users_result = provider.fetch(
                "SELECT * FROM users WHERE active = ?",
                params=[True]
            )
            
            print(f"Found {len(active_users_result.data)} active users")
            
            # Fetch users with posts (JOIN)
            print("\nFetching users with their post counts...")
            join_result = provider.fetch('''
                SELECT u.name, u.email, COUNT(p.id) as post_count
                FROM users u
                LEFT JOIN posts p ON u.id = p.user_id
                GROUP BY u.id, u.name, u.email
                ORDER BY post_count DESC
            ''')
            
            print("Users and their post counts:")
            for row in join_result.data:
                print(f"  - {row['name']}: {row['post_count']} posts")
            
            # Insert a new user
            print("\nInserting a new user...")
            affected_rows = provider.execute(
                "INSERT INTO users (name, email, age, active) VALUES (?, ?, ?, ?)",
                params=['Frank Miller', 'frank@example.com', 45, True]
            )
            print(f"Inserted {affected_rows} row(s)")
            
            # Update user
            print("\nUpdating user age...")
            affected_rows = provider.execute(
                "UPDATE users SET age = ? WHERE name = ?",
                params=[29, 'Alice Johnson']
            )
            print(f"Updated {affected_rows} row(s)")
            
            # Delete inactive users
            print("\nDeleting inactive users...")
            affected_rows = provider.execute(
                "DELETE FROM users WHERE active = ?",
                params=[False]
            )
            print(f"Deleted {affected_rows} row(s)")
            
            # Use transaction for multiple operations
            print("\nUsing transaction for multiple operations...")
            with provider.transaction():
                # Insert multiple posts
                posts_data = [
                    (1, 'New Post 1', 'Content for new post 1'),
                    (1, 'New Post 2', 'Content for new post 2'),
                    (2, 'Another Post', 'More content here')
                ]
                
                affected_rows = provider.execute_many(
                    "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
                    params_list=posts_data
                )
                print(f"Inserted {affected_rows} posts in transaction")
            
            # Verify the results
            print("\nFinal user count:")
            final_users = provider.fetch("SELECT COUNT(*) as count FROM users")
            print(f"Total users: {final_users.data[0]['count']}")
    
    except Exception as e:
        print(f"Error: {e}")


async def async_database_example():
    """Example of asynchronous database usage."""
    print("\n=== Asynchronous Database Example ===")
    
    # Configure async database connection
    config = DatabaseConfig(
        database_type='sqlite',
        database='sample.db'
    )
    
    # Create async provider
    provider = Database_AsyncDataProvider(config)
    
    try:
        async with provider.async_connection():
            # Fetch users asynchronously
            print("Fetching users asynchronously...")
            users_result = await provider.fetch("SELECT * FROM users")
            
            print(f"Found {len(users_result.data)} users")
            
            # Fetch posts with user information
            print("\nFetching posts with user information...")
            posts_with_users = await provider.fetch('''
                SELECT p.title, p.content, u.name as author_name, u.email as author_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 5
            ''')
            
            print("Recent posts:")
            for post in posts_with_users.data:
                print(f"  - {post['title']} by {post['author_name']}")
                print(f"    Content: {post['content'][:50]}...")
            
            # Custom validation example
            print("\nUsing custom validation...")
            
            original_validate = provider.validate
            
            async def validate_user_data(data):
                # Only accept users who are active and under 40
                return data.get('active', False) and data.get('age', 0) < 40
            
            provider.validate = validate_user_data
            
            young_users = await provider.fetch("SELECT * FROM users")
            print(f"Found {len(young_users.data)} young active users")
            
            # Restore original validation
            provider.validate = original_validate
    
    except Exception as e:
        print(f"Error: {e}")


def postgres_example():
    """Example for PostgreSQL (requires PostgreSQL setup)."""
    print("\n=== PostgreSQL Example (Configuration Only) ===")
    
    # This is just a configuration example
    # You would need to have PostgreSQL running and install psycopg2
    postgres_config = DatabaseConfig(
        database_type='postgres',
        host='localhost',
        port=5432,
        database='myapp',
        username='postgres',
        password='password',
        ssl_mode='prefer'
    )
    
    print("PostgreSQL configuration created:")
    print(f"  Host: {postgres_config.host}")
    print(f"  Database: {postgres_config.database}")
    print(f"  Username: {postgres_config.username}")
    
    # Uncomment below to actually use PostgreSQL:
    # provider = DatabaseProvider(postgres_config)
    # with provider.connection():
    #     result = provider.fetch("SELECT version()")


def error_handling_example():
    """Example of error handling with database provider."""
    print("\n=== Database Error Handling Example ===")
    
    # Try to connect to non-existent database
    config = DatabaseConfig(
        database_type='sqlite',
        database='nonexistent.db'
    )
    
    provider = Database_DataProvider(config)
    
    try:
        with provider.connection():
            # This should work (creates file if it doesn't exist)
            result = provider.fetch("SELECT 1 as test")
            print("Connection successful")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Try invalid SQL
    config_valid = DatabaseConfig(
        database_type='sqlite',
        database='sample.db'
    )
    
    provider_valid = Database_DataProvider(config_valid)
    
    try:
        with provider_valid.connection():
            # This should fail
            result = provider_valid.fetch("SELECT * FROM nonexistent_table")
    except Exception as e:
        print(f"SQL error caught: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Run synchronous examples
    sync_database_example()
    error_handling_example()
    postgres_example()
    
    # Run asynchronous example
    asyncio.run(async_database_example())
    
    print("\n=== All Database Examples Completed ===")
