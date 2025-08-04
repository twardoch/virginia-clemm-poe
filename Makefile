# Makefile for Virginia Clemm Poe development tasks
# Provides convenient shortcuts for common development operations

.PHONY: help install lint format type-check security test test-unit test-integration clean build docs pre-commit setup-dev all-checks

# Default target
help:
	@echo "Virginia Clemm Poe Development Commands"
	@echo "======================================="
	@echo ""
	@echo "Setup:"
	@echo "  install      Install project dependencies"
	@echo "  setup-dev    Set up development environment with pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run comprehensive linting checks"
	@echo "  format       Auto-format code with ruff"
	@echo "  type-check   Run mypy type checking"
	@echo "  security     Run security scans (bandit + safety)"
	@echo "  all-checks   Run all code quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests with coverage"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration  Run integration tests (requires POE_API_KEY)"
	@echo ""
	@echo "Build:"
	@echo "  build        Build package for distribution"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Git:"
	@echo "  pre-commit   Run pre-commit hooks on all files"

# Setup and installation
install:
	@echo "📦 Installing dependencies..."
	uv sync --all-extras --dev

setup-dev: install
	@echo "🔧 Setting up development environment..."
	uvx pre-commit install
	@echo "✅ Development environment ready!"

# Code quality checks
lint:
	@echo "🔍 Running ruff linting..."
	uvx ruff check src/ tests/
	@echo "📝 Checking docstrings..."
	uvx pydocstyle src/ --config=pyproject.toml

format:
	@echo "🎨 Formatting code with ruff..."
	uvx ruff format src/ tests/
	uvx ruff check --fix src/ tests/

type-check:
	@echo "🔍 Running mypy type checking..."
	uvx mypy src/

security:
	@echo "🔒 Running security checks..."
	uvx bandit -r src/ -c pyproject.toml
	@echo "🛡️  Checking dependencies for vulnerabilities..."
	uvx safety check --json || echo "⚠️  Safety check completed with warnings"

all-checks: lint type-check security
	@echo "✅ All code quality checks completed!"

# Testing
test:
	@echo "🧪 Running all tests with coverage..."
	uvx pytest tests/ --cov=virginia_clemm_poe --cov-report=term-missing --cov-report=html

test-unit:
	@echo "🧪 Running unit tests..."
	uvx pytest tests/ -m "not integration" --cov=virginia_clemm_poe --cov-report=term-missing

test-integration:
	@echo "🧪 Running integration tests..."
	@if [ -z "$$POE_API_KEY" ]; then \
		echo "❌ POE_API_KEY environment variable is required for integration tests"; \
		exit 1; \
	fi
	uvx pytest tests/ -m "integration" --tb=short

# Build and distribution
build: clean
	@echo "📦 Building package..."
	uv build
	@echo "🔍 Checking package..."
	uvx twine check dist/*

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Git hooks
pre-commit:
	@echo "🎯 Running pre-commit hooks on all files..."
	uvx pre-commit run --all-files

# Comprehensive development workflow
dev-check: format all-checks test-unit
	@echo "🎉 Development checks completed successfully!"

# CI simulation
ci-check: all-checks test build
	@echo "🎉 CI checks completed successfully!"