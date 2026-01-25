# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-14

### Added
- Initial release of Data Retrieval Module
- Synchronous `DataProvider` abstract base class
- Asynchronous `AsyncDataProvider` abstract base class
- Standardized `QueryResult` data container
- Connection management with context managers
- Built-in retry logic with configurable parameters
- Hook methods for validation and transformation
- Comprehensive exception hierarchy
- Full type hints and generic support
- Comprehensive unit test suite (41 tests)
- PyPI package configuration
- Development tools configuration (black, isort, mypy, pytest)

### Features
- **Dual API Support**: Both sync and async interfaces
- **Connection Management**: Automatic connection handling
- **Retry Logic**: Configurable retry mechanisms
- **Type Safety**: Full type annotations
- **Error Handling**: Specific exception types
- **Testing**: Complete test coverage
- **Documentation**: Comprehensive README and API docs

### Documentation
- Complete README with usage examples
- API documentation for all classes
- Development setup instructions
- Contributing guidelines

### Development
- Setuptools and pyproject.toml configuration
- Pre-commit hooks configuration
- CI/CD ready setup
- Package publishing configuration

## [1.0.1] - 2026-01-25

### Added
- Foreign Exchange data provider module
  - `Forex_DataProvider_Base` abstract base class for forex data providers
  - `ForexPython_DataProvider` concrete implementation using Python libraries
  - `Forex_DataProvider_Wrapper` wrapper for enhanced functionality
- Utility modules
  - `date_utils` module for date/time utilities
- Enhanced data provider wrapper functionality
- Examples for forex data sources

### Features
- **Forex Data Support**: Complete foreign exchange data provider framework
- **Utility Functions**: Date and time utilities for data processing
- **Enhanced Wrappers**: Improved data provider wrapper capabilities
- **Example Code**: Forex data source examples and usage patterns

### Documentation
- Added forex provider documentation
- Updated package exports to include new modules
- Enhanced examples with forex data sources

## [Unreleased]

### Planned
- Additional data source implementations
- Performance benchmarks
- Advanced caching mechanisms
- Metrics and monitoring support
- Integration with popular ORMs

---

## Version History

### v1.0.0-alpha (2025-11-13)
- Initial concept and design
- Basic abstract classes
- Core functionality implementation

### v1.0.0-beta (2025-12-01)
- Added async support
- Improved error handling
- Enhanced testing coverage
- Documentation improvements

### v1.0.0 (2026-01-14)
- Production-ready release
- Complete test suite
- PyPI publishing configuration
- Final documentation
