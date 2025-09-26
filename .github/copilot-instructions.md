# syntest-lib - Copilot Instructions

This is a Python library for managing Kentik synthetic tests, labels, and sites through CSV files and programmatic APIs.

## Project Overview

- **Purpose**: Simplified synthetic test management for enterprise monitoring
- **Key Feature**: CSV-based bulk test management with automatic resource creation
- **API Integration**: Kentik Synthetics, Labels, and Sites APIs (v202309)
- **Architecture**: Clean separation between API client, test generators, and CSV managers

## Development Guidelines

When working on this project:

1. **Follow existing patterns**: The codebase uses Pydantic models for API serialization and clear separation of concerns
2. **CSV-first approach**: The CSV management system is the primary use case - keep it simple and powerful
3. **Rate limiting**: All API interactions include automatic rate limiting and retry logic
4. **DNS focus**: Special attention to DNS and DNS grid test types
5. **Enterprise scale**: Design for hundreds of tests across multiple sites

## Key Components

- `SyntheticsClient`: Main API client with rate limiting and error handling
- `TestGenerator`: Creates test configurations with sensible defaults
- `CSVTestManager`: Bulk test management from CSV files
- `models.py`: Pydantic models matching Kentik API schemas
- `utils.py`: Helper functions for filtering and analysis

## Code Style

- Use type hints throughout
- Comprehensive error handling with informative messages
- Clear logging for debugging and audit trails
- Minimal required parameters with sensible defaults