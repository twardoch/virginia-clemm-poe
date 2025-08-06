# Virginia Clemm Poe 

**Virginia Clemm Poe** is a Python package that provides programmatic access to comprehensive Poe.com model data with pricing information. It acts as a companion tool to the official Poe API by fetching, maintaining, and enriching model data through web scraping, with a special focus on capturing detailed pricing information not available through the API alone.

[Poe Models](models/index.md){ .md-button .md-button--primary } [Models JSON](https://raw.githubusercontent.com/twardoch/virginia-clemm-poe/refs/heads/main/src/virginia_clemm_poe/data/poe_models.json){ .md-button }

The models shown here is a snapshot of the models that are available on [api.poe.com](https://creator.poe.com/docs/external-applications/openai-compatible-api), the OpenAI-compatible API that you can use with your Poe.com [API key](https://poe.com/api_key) if you’re a Poe subscriber. 

The JSON at `https://raw.githubusercontent.com/twardoch/virginia-clemm-poe/refs/heads/main/src/virginia_clemm_poe/data/poe_models.json` is based on `https://api.poe.com/v1/models` but is extended with pricing info and description.  

The tools in this repository can be used to update the JSON file with the latest pricing info and description. 

## Getting Started

1. **[Introduction and Overview](chapter1-introduction.md)** - Learn about the package's purpose, architecture, and core concepts
2. **[Installation and Setup](chapter2-installation.md)** - Step-by-step installation guide and initial configuration
3. **[Quick Start Guide](chapter3-quickstart.md)** - Get up and running with basic examples and common use cases

## Usage Guides

4. **[Python API Reference](chapter4-api.md)** - Complete Python API documentation with examples
5. **[CLI Usage and Commands](chapter5-cli.md)** - Command-line interface reference and usage patterns
6. **[Data Models and Structure](chapter6-models.md)** - Understanding the data structures and Pydantic models

## Advanced Topics

7. **[Browser Management and Web Scraping](chapter7-browser.md)** - Deep dive into web scraping functionality and browser automation
8. **[Configuration and Advanced Usage](chapter8-configuration.md)** - Advanced configuration options and customization
9. **[Troubleshooting and FAQ](chapter9-troubleshooting.md)** - Common issues, solutions, and frequently asked questions

## Quick Example

```python
from virginia_clemm_poe import api

# Search for Claude models
claude_models = api.search_models(query="claude")

# Get specific model with pricing
model = api.get_model_by_id("claude-3-opus")
if model.pricing:
    print(f"Input cost: {model.pricing.details['Input (text)']}")

# List all available models
all_models = api.list_models()
print(f"Total models available: {len(all_models)}")
```

## CLI Quick Start

```bash
# Setup browser for web scraping
virginia-clemm-poe setup

# Update model data with pricing
POE_API_KEY=your_key virginia-clemm-poe update --pricing

# Search for models
virginia-clemm-poe search "gpt-4"
```

## Project Links

- **GitHub Repository**: [terragonlabs/virginia-clemm-poe](https://github.com/terragonlabs/virginia-clemm-poe)
- **PyPI Package**: [virginia-clemm-poe](https://pypi.org/project/virginia-clemm-poe/)
- **Issues & Support**: [GitHub Issues](https://github.com/terragonlabs/virginia-clemm-poe/issues)

---

*Named after Edgar Allan Poe's wife and cousin, Virginia Clemm Poe, this package serves as a faithful companion to the Poe platform, just as she was to the great poet.*