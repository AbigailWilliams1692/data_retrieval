# Makefile for Data Retrieval Module Testing
# Author: AbigailWilliams1692
# Created: 2025-11-13
# Updated: 2025-01-14

.PHONY: help test test-unit test-integration test-async test-coverage test-all clean install format lint

# Default target
help:
	@echo "Available commands:"
	@echo "  help          - Show this help message"
	@echo "  install       - Install test dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-async    - Run async tests only"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  test-all      - Run all test suites with coverage"
	@echo "  format        - Format code with black and isort"
	@echo "  lint          - Run linting with flake8 and mypy"
	@echo "  clean         - Clean test artifacts"

# Installation
install:
	pip install -r requirements-test.txt

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "unit"

test-integration:
	pytest tests/ -v -m "integration"

test-async:
	pytest tests/ -v -m "async_test"

test-coverage:
	pytest tests/ --cov=data_retrieval --cov-report=html --cov-report=term

test-all:
	pytest tests/ --cov=data_retrieval --cov-report=html --cov-report=term --cov-report=xml

# Code quality
format:
	black tests/ data_retrieval/
	isort tests/ data_retrieval/

lint:
	flake8 tests/ data_retrieval/
	mypy data_retrieval/

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ pytest.xml .pytest_cache/ .mypy_cache/

# Development helpers
dev-test: format lint test

ci-test: install test-all
