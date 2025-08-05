# Chapter 2: Installation and Setup

## System Requirements

### Python Version
- **Python 3.12+** is required
- The package uses modern Python features and type hints

### Operating System
- **Linux** (recommended for production)
- **macOS** (fully supported)
- **Windows** (supported with some limitations)

### Browser Requirements
- **Chrome or Chromium** browser must be installed
- The package uses Playwright for web scraping, which requires a Chromium-based browser
- Browser installation is handled automatically by the package

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
pip install virginia-clemm-poe
```

For users with `uv` (recommended for faster dependency resolution):

```bash
uv pip install virginia-clemm-poe
```

### Method 2: Development Installation

If you want to contribute or use the latest development version:

```bash
git clone https://github.com/terragonlabs/virginia-clemm-poe.git
cd virginia-clemm-poe
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Method 3: Direct from GitHub

```bash
pip install git+https://github.com/terragonlabs/virginia-clemm-poe.git
```

## Initial Setup

### 1. Browser Setup

After installation, you need to set up the browser for web scraping:

```bash
virginia-clemm-poe setup
```

This command will:
- Download and configure Playwright
- Install necessary browser dependencies
- Verify browser functionality
- Create initial configuration files

!!! note "Browser Setup"
    The setup process downloads a Chromium browser (~100MB) that's isolated from your system browser. This ensures consistent scraping behavior across different environments.

### 2. API Key Configuration

To use the full functionality, you need a Poe API key:

#### Getting a Poe API Key

1. Visit [Poe.com](https://poe.com)
2. Sign in to your account
3. Navigate to API settings
4. Generate a new API key
5. Copy the key for configuration

#### Setting the API Key

You can provide the API key in several ways:

**Option 1: Environment Variable (Recommended)**
```bash
export POE_API_KEY="your_api_key_here"
```

**Option 2: Configuration File**
```bash
virginia-clemm-poe config set-api-key your_api_key_here
```

**Option 3: Runtime Parameter**
```bash
virginia-clemm-poe update --api-key your_api_key_here
```

### 3. Verify Installation

Test that everything is working correctly:

```bash
# Check package version
virginia-clemm-poe --version

# Test basic functionality
virginia-clemm-poe search "claude"

# Run a complete health check
virginia-clemm-poe diagnose
```

## Configuration Options

### Configuration File Location

The package stores configuration in:
- **Linux/macOS**: `~/.config/virginia-clemm-poe/config.json`
- **Windows**: `%APPDATA%\virginia-clemm-poe\config.json`

### Configuration Structure

```json
{
  "api_key": "your_poe_api_key",
  "browser": {
    "headless": true,
    "timeout": 30000,
    "user_agent": "custom_user_agent"
  },
  "cache": {
    "enabled": true,
    "max_age": 3600
  },
  "logging": {
    "level": "INFO",
    "file": "~/.local/share/virginia-clemm-poe/logs/app.log"
  }
}
```

### Environment Variables

The package respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POE_API_KEY` | Your Poe API key | None (required) |
| `VCP_HEADLESS` | Run browser in headless mode | `true` |
| `VCP_TIMEOUT` | Browser timeout in milliseconds | `30000` |
| `VCP_LOG_LEVEL` | Logging level | `INFO` |
| `VCP_CACHE_DIR` | Cache directory location | Platform default |

## Data Storage

### Default Locations

The package stores data in platform-appropriate locations:

**Linux/macOS:**
- **Data**: `~/.local/share/virginia-clemm-poe/`
- **Config**: `~/.config/virginia-clemm-poe/`
- **Cache**: `~/.cache/virginia-clemm-poe/`
- **Logs**: `~/.local/share/virginia-clemm-poe/logs/`

**Windows:**
- **Data**: `%LOCALAPPDATA%\virginia-clemm-poe\`
- **Config**: `%APPDATA%\virginia-clemm-poe\`
- **Cache**: `%LOCALAPPDATA%\virginia-clemm-poe\cache\`
- **Logs**: `%LOCALAPPDATA%\virginia-clemm-poe\logs\`

### Dataset Location

The main model dataset is stored as a JSON file:
```
~/.local/share/virginia-clemm-poe/poe_models.json
```

## Troubleshooting Installation

### Common Issues

#### 1. Python Version Error
```
ERROR: Package requires Python 3.12+
```
**Solution**: Upgrade your Python installation or use a version manager like `pyenv`.

#### 2. Browser Setup Fails
```
ERROR: Failed to install browser dependencies
```
**Solutions**:
- Ensure you have internet connectivity
- Run with elevated permissions if needed
- Check disk space (browser download requires ~100MB)

#### 3. Permission Errors
```
ERROR: Permission denied writing to config directory
```
**Solutions**:
- Check file permissions on config directories
- Run installation with appropriate user permissions
- Manually create config directories if needed

#### 4. Network Issues
```
ERROR: Unable to connect to Poe API
```
**Solutions**:
- Check internet connectivity
- Verify API key is correct
- Check if your network blocks API requests

### Debug Installation

For detailed debugging during installation:

```bash
# Enable verbose logging
export VCP_LOG_LEVEL=DEBUG

# Run installation with debug output
virginia-clemm-poe setup --verbose

# Check system compatibility
virginia-clemm-poe diagnose --full
```

## Upgrading

### Upgrade Package

```bash
pip install --upgrade virginia-clemm-poe
```

### Upgrade Browser Dependencies

```bash
virginia-clemm-poe setup --force
```

### Migrate Configuration

When upgrading from older versions, you may need to migrate configuration:

```bash
virginia-clemm-poe config migrate
```

## Uninstallation

### Remove Package

```bash
pip uninstall virginia-clemm-poe
```

### Clean Up Data (Optional)

To remove all data and configuration files:

```bash
# Remove data directories
rm -rf ~/.local/share/virginia-clemm-poe
rm -rf ~/.config/virginia-clemm-poe
rm -rf ~/.cache/virginia-clemm-poe

# On Windows, remove:
# %LOCALAPPDATA%\virginia-clemm-poe
# %APPDATA%\virginia-clemm-poe
```

## Next Steps

With the package installed and configured, you're ready to:

1. Follow the [Quick Start Guide](chapter3-quickstart.md) for basic usage
2. Learn about the [Python API](chapter4-api.md) for programmatic access
3. Explore [CLI Commands](chapter5-cli.md) for command-line usage

!!! tip "Performance Optimization"
    For best performance, consider running the initial data update during off-peak hours as it involves scraping hundreds of model pages:
    ```bash
    POE_API_KEY=your_key virginia-clemm-poe update --all
    ```