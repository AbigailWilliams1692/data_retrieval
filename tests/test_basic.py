#!/usr/bin/env python3
"""
Test suite for Data Retrieval Module.
"""

import pytest
import sys
import os

# Add the package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test basic imports
def test_basic_imports():
    """Test that basic classes can be imported."""
    from data_retrieval import DataProvider, DataModule
    from data_retrieval.model.exceptions import DataProviderError
    
    assert DataProvider is not None
    assert DataModule is not None
    assert DataProviderError is not None

# Test version
def test_version():
    """Test that version is defined."""
    import data_retrieval
    
    assert hasattr(data_retrieval, '__version__')
    assert data_retrieval.__version__ == "1.0.0"

# Test package structure
def test_package_structure():
    """Test that package structure is correct."""
    import data_retrieval
    
    # Check that main classes are available
    assert hasattr(data_retrieval, 'DataProvider')
    assert hasattr(data_retrieval, 'DataModule')
    
    # Check that providers are available
    assert hasattr(data_retrieval, 'RestAPI_DataProvider')
    assert hasattr(data_retrieval, 'Database_DataProvider')
    
    # Check that exceptions are available
    assert hasattr(data_retrieval, 'DataProviderError')
    assert hasattr(data_retrieval, 'DataFetchError')
