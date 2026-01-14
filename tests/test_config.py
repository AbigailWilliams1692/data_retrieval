#######################################################################
# Project: Data Retrieval Module
# File: test_config.py
# Description: Test configuration and utilities
# Author: AbigailWilliams1692
# Created: 2026-01-14
# Updated: 2026-01-14
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import os
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

#######################################################################
# Test Configuration
#######################################################################
TEST_CONFIG = {
    "database": {
        "host": os.getenv("TEST_DB_HOST", "localhost"),
        "port": int(os.getenv("TEST_DB_PORT", "5432")),
        "name": os.getenv("TEST_DB_NAME", "test_db"),
        "user": os.getenv("TEST_DB_USER", "test_user"),
        "password": os.getenv("TEST_DB_PASSWORD", "test_pass"),
    },
    "api": {
        "base_url": os.getenv("TEST_API_URL", "http://localhost:8000"),
        "timeout": int(os.getenv("TEST_API_TIMEOUT", "30")),
        "api_key": os.getenv("TEST_API_KEY", "test_key"),
    },
    "logging": {
        "level": os.getenv("TEST_LOG_LEVEL", "DEBUG"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },
}

#######################################################################
# Test Utilities
#######################################################################
def get_test_config(section: str = None):
    """Get test configuration.
    
    Args:
        section: Configuration section to return (optional)
        
    Returns:
        Configuration dictionary or specific section
    """
    if section:
        return TEST_CONFIG.get(section, {})
    return TEST_CONFIG

def setup_test_logging():
    """Set up logging for tests."""
    import logging
    
    config = get_test_config("logging")
    logging.basicConfig(
        level=getattr(logging, config["level"]),
        format=config["format"]
    )

def create_test_data(count: int = 10):
    """Create test data for testing purposes.
    
    Args:
        count: Number of test items to create
        
    Returns:
        List of test data items
    """
    return [
        {
            "id": f"test_{i}",
            "name": f"Test Item {i}",
            "value": i * 10,
            "active": i % 2 == 0
        }
        for i in range(1, count + 1)
    ]
