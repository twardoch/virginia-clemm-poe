# Contributing to Virginia Clemm Poe

Thank you for your interest in contributing to Virginia Clemm Poe! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Architecture Guidelines](#architecture-guidelines)

## Code of Conduct

Please be respectful and professional in all interactions. We welcome contributions from developers of all skill levels and backgrounds.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` package manager
- Chrome or Chromium browser (for web scraping functionality)
- Poe API key for testing

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/virginia-clemm-poe.git
   cd virginia-clemm-poe
   ```

## Development Setup

### Environment Setup

1. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   export POE_API_KEY=your_poe_api_key_here
   ```

### Running the Application

```bash
# Update model data
POE_API_KEY=your_key python -m virginia_clemm_poe update --all

# Search for models
python -m virginia_clemm_poe search "claude"

# Run tests
python -m pytest
```

## Code Style and Standards

### Python Code Standards

We follow modern Python best practices:

- **PEP 8**: Standard Python formatting and naming conventions
- **PEP 20**: Zen of Python - simple, explicit, readable code
- **PEP 257**: Docstring conventions with comprehensive documentation
- **Type hints**: Use Python 3.12+ type hints throughout
- **Modern syntax**: f-strings, pattern matching, pathlib

### Code Quality Requirements

#### Docstrings
- All public functions, classes, and methods must have comprehensive docstrings
- Include purpose, parameters, return values, examples, and notes
- Complex logic should be thoroughly documented with workflow explanations

#### Error Handling
- Use proper exception chaining with `raise ... from e`
- Implement graceful fallbacks and recovery strategies
- Provide clear error messages with context

#### Function Design
- Keep functions focused and under 50 lines when possible
- Use the Extract Method pattern for complex operations
- Follow Single Responsibility Principle
- Apply DRY principle for repeated logic

#### Variable Naming
- Use descriptive names: `collection_data` instead of `data`
- Avoid single-letter variables: `model` instead of `m`
- Use constants for magic numbers

### File Organization

#### File Path Tracking
- Every source file must include a `this_file` comment near the top:
  ```python
  # this_file: src/virginia_clemm_poe/module_name.py
  ```

#### Module Structure
```
src/virginia_clemm_poe/
├── __main__.py          # CLI entry point
├── api.py              # Public API functions
├── config.py           # Configuration constants
├── models.py           # Pydantic data models
├── updater.py          # Core update logic
├── browser_manager.py  # Browser automation
├── browser_pool.py     # Connection pooling
├── type_guards.py      # Runtime type validation
├── exceptions.py       # Custom exceptions
└── utils/              # Utility modules
    ├── cache.py        # Caching utilities
    ├── crash_recovery.py # Error recovery
    ├── logger.py       # Logging utilities
    ├── memory.py       # Memory management
    └── timeout.py      # Timeout handling
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=virginia_clemm_poe

# Run specific test file
python -m pytest tests/test_api.py
```

### Test Requirements

- All new functionality must include tests
- Aim for high test coverage (>85%)
- Use meaningful test names that describe behavior
- Mock external dependencies (API calls, browser operations)

### Test Structure

```python
def test_search_models_returns_matching_results():
    """Test that search_models returns models matching the query."""
    # Arrange
    models = [...]
    
    # Act
    results = search_models("claude")
    
    # Assert
    assert len(results) > 0
    assert all("claude" in model.id.lower() for model in results)
```

## Pull Request Process

### Before Submitting

1. **Code Quality**: Run linting and formatting:
   ```bash
   uvx ruff check --fix src/
   uvx ruff format src/
   uvx mypy src/
   ```

2. **Tests**: Ensure all tests pass:
   ```bash
   python -m pytest
   ```

3. **Documentation**: Update relevant documentation files

### Pull Request Guidelines

1. **Title**: Use clear, descriptive titles
   - ✅ "Add comprehensive docstrings for complex parsing logic"
   - ❌ "Fix stuff"

2. **Description**: Include:
   - Summary of changes
   - Motivation for the change  
   - Any breaking changes
   - Test coverage notes

3. **Commits**: 
   - Use meaningful commit messages
   - Keep commits atomic and focused
   - Squash related commits before submitting

4. **Size**: Keep PRs focused and reasonably sized
   - Prefer multiple small PRs over one large PR
   - Split unrelated changes into separate PRs

### Review Process

- All PRs require at least one review
- Address review feedback promptly
- Maintain a collaborative and respectful tone
- Be open to suggestions and improvements

## Issue Reporting

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages and stack traces

### Feature Requests

Include:
- Clear description of the desired functionality
- Use cases and motivation
- Potential implementation approach
- Any relevant examples or references

### Labels

Use appropriate labels:
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation improvements
- `help wanted` - Good for new contributors
- `priority:high` - Critical issues

## Architecture Guidelines

### Browser Management

- Use the browser pool for efficient connection reuse
- Implement proper timeout handling for all browser operations
- Include crash detection and recovery mechanisms
- Apply memory management for long-running operations

### API Integration

- Cache API responses appropriately (600s TTL for model lists)
- Implement proper rate limiting and error handling
- Use structured logging for all API operations
- Validate all external data with type guards

### Data Management

- Use Pydantic models for all data structures
- Implement comprehensive validation with helpful error messages
- Cache scraped data to minimize redundant requests
- Handle partial failures gracefully

### Performance Considerations

- Use async/await for I/O operations
- Implement memory monitoring for bulk operations
- Apply connection pooling for browser operations
- Cache expensive operations with appropriate TTLs

## Getting Help

- **Questions**: Open a GitHub issue with the `question` label
- **Discussions**: Use GitHub Discussions for broader topics
- **Bug Reports**: Create detailed issues with reproduction steps

Thank you for contributing to Virginia Clemm Poe! Your contributions help make this tool more useful for the community.