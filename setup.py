#!/usr/bin/env python
"""
Setup script for Data Retrieval Module Package.
Author: AbigailWilliams1692
Created: 2026-01-14
Updated: 2026-01-14
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Data Retrieval Module - A standardized interface for data providers"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="data-retrieval-module",
    version="1.0.0",
    author="AbigailWilliams1692",
    author_email="abigail.williams@example.com",
    description="A standardized interface for data providers with sync and async support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/AbigailWilliams1692/data-retrieval-module",
    project_urls={
        "Bug Tracker": "https://github.com/AbigailWilliams1692/data-retrieval-module/issues",
        "Documentation": "https://github.com/AbigailWilliams1692/data-retrieval-module/wiki",
        "Source Code": "https://github.com/AbigailWilliams1692/data-retrieval-module",
    },
    packages=find_packages(exclude=["tests*", "benchmarks*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio-mqtt>=0.13.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "aiohttp>=3.8.0",
            "asyncio-mqtt>=0.13.0",
        ],
    },
    keywords="data retrieval, provider, async, sync, database, api",
    include_package_data=True,
    package_data={
        "data_retrieval": ["py.typed"],
    },
    zip_safe=False,
)
