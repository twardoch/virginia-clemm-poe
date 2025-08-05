# Chapter 5: CLI Usage and Commands

## Overview

Virginia Clemm Poe provides a comprehensive command-line interface built with Python Fire and Rich for beautiful terminal output. The CLI is designed for both interactive exploration and automation workflows.

## Command Structure

All commands follow the pattern:
```bash
virginia-clemm-poe <command> [options]
```

Get help for any command:
```bash
virginia-clemm-poe <command> --help
```

## Core Commands

### Setup and Configuration

#### `setup`
Set up Chrome browser for web scraping - required before first update.

```bash
# Basic setup (recommended)
virginia-clemm-poe setup

# Troubleshooting setup with verbose output
virginia-clemm-poe setup --verbose
```

**What it does:**
- Detects existing Chrome/Chromium installations
- Downloads Chrome for Testing if needed (~200MB)
- Configures browser automation with DevTools Protocol
- Verifies browser can launch successfully

**System requirements:**
- Available disk space: ~200MB
- Network access for browser download
- Write permissions to cache directory

**Installation locations:**
- **macOS**: `~/Library/Caches/virginia-clemm-poe/`
- **Linux**: `~/.cache/virginia-clemm-poe/`
- **Windows**: `%LOCALAPPDATA%\virginia-clemm-poe\`

#### `status`
Check system health and data freshness.

```bash
# Quick health check
virginia-clemm-poe status

# Detailed system diagnosis
virginia-clemm-poe status --verbose
```

**Checks performed:**
- ✅ Browser installation and accessibility
- ✅ Model dataset existence and freshness
- ✅ POE_API_KEY environment variable
- ✅ System dependencies

**Sample output:**
```
Virginia Clemm Poe Status

Browser Status:
✓ Browser is ready
  Path: /Users/user/.cache/virginia-clemm-poe/chrome-mac/chrome
  User Data: /Users/user/.cache/virginia-clemm-poe/user-data

Data Status:
✓ Model data found
  Path: ~/.local/share/virginia-clemm-poe/poe_models.json
  Total models: 244
  With pricing: 239
  With bot info: 235
  Data is 2 days old

API Key Status:
✓ POE_API_KEY is set
```

#### `doctor`
Comprehensive diagnostic tool for troubleshooting.

```bash
# Run all diagnostic checks
virginia-clemm-poe doctor

# Verbose diagnosis for support requests
virginia-clemm-poe doctor --verbose
```

**Diagnostic checks:**
1. **Python Version**: Ensures Python 3.12+ compatibility
2. **API Key**: Validates POE_API_KEY and tests connectivity
3. **Browser**: Verifies browser installation and launch capability
4. **Network**: Tests connectivity to poe.com
5. **Dependencies**: Checks all required packages
6. **Data File**: Validates JSON structure and content

**Exit codes:**
- `0`: All checks passed
- `1`: Issues found that need attention

### Data Management

#### `update`
Fetch latest model data from Poe - run weekly or when new models appear.

```bash
# Update all data (default)
POE_API_KEY=your_key virginia-clemm-poe update

# Update only pricing information
virginia-clemm-poe update --pricing

# Update only bot information (faster)
virginia-clemm-poe update --info

# Force update all models
virginia-clemm-poe update --force

# Use custom API key
virginia-clemm-poe update --api_key your_key

# Debug port conflicts
virginia-clemm-poe update --debug_port 9223

# Troubleshooting with verbose output
virginia-clemm-poe update --verbose
```

**Update process:**
1. Fetches all models from Poe API
2. Launches Chrome for web scraping
3. Visits each model's page to extract pricing and metadata
4. Saves enriched dataset to local JSON file

**Parameters:**
- `--info`: Update only bot information
- `--pricing`: Update only pricing information  
- `--all`: Update both (default)
- `--force`: Update even models with existing data
- `--api_key`: Override POE_API_KEY environment variable
- `--debug_port`: Chrome DevTools port (default: 9222)
- `--verbose`: Enable detailed logging

**Performance:**
- Full update: 5-15 minutes for ~240 models
- Partial updates: 1-5 minutes depending on changes
- Incremental: Only updates models missing data

#### `clear-cache`
Clear cache and stored data.

```bash
# Clear all cache (default)
virginia-clemm-poe clear-cache

# Clear only model data
virginia-clemm-poe clear-cache --data

# Clear only browser cache
virginia-clemm-poe clear-cache --browser

# Verbose cache clearing
virginia-clemm-poe clear-cache --verbose
```

**Cache types:**
- **Model data**: Local JSON dataset
- **Browser cache**: Chrome user data and profiles

#### `cache`
Monitor cache performance and statistics.

```bash
# Show cache statistics
virginia-clemm-poe cache

# Clear all caches
virginia-clemm-poe cache --clear

# Verbose cache management
virginia-clemm-poe cache --verbose
```

**Statistics shown:**
- Cache hit rates and miss rates
- Total requests and performance
- Memory usage and evictions
- Expired entry cleanups

### Data Query Commands

#### `search`
Find models by name or ID - primary discovery command.

```bash
# Find Claude models
virginia-clemm-poe search claude

# Find GPT models with bot info
virginia-clemm-poe search gpt --show_bot_info

# Search without pricing data
virginia-clemm-poe search vision --no-show_pricing

# Verbose search for debugging
virginia-clemm-poe search claude --verbose
```

**Search features:**
- Case-insensitive substring matching
- Searches both model IDs and names
- Fuzzy matching for partial terms
- Formatted table output with Rich

**Parameters:**
- `query`: Search term (required)
- `--show_pricing`: Display pricing columns (default: True)
- `--show_bot_info`: Include creator and description (default: False)
- `--verbose`: Enable detailed logging

**Sample output:**
```
                Models matching 'claude'                
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID              ┃ Created    ┃ Input ┃ Output ┃ Pricing             ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Claude-3-Opus   │ 2024-02-29 │ text  │ text   │ 15 points/message  │
│ Claude-3-Sonnet │ 2024-03-04 │ text  │ text   │ 10 points/message  │
└─────────────────┴────────────┴───────┴────────┴─────────────────────┘
Found 2 models
```

#### `list`
List all available models with summary statistics.

```bash
# Show model summary
virginia-clemm-poe list

# Show only models with pricing
virginia-clemm-poe list --with_pricing

# Limit results
virginia-clemm-poe list --limit 10

# Verbose listing
virginia-clemm-poe list --verbose
```

**Parameters:**
- `--with_pricing`: Filter to models with pricing data
- `--limit`: Maximum number of models to show
- `--verbose`: Enable detailed logging

**Sample output:**
```
          Poe Models Summary           
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Total Models ┃ With Pricing ┃ Need Update ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 244          │ 239          │ 5           │
└──────────────┴─────────────┴─────────────┘

Showing 244 models:
✓ Claude-3-Opus
✓ Claude-3-Sonnet
✗ NewModel-Beta
...
```

## Environment Variables

The CLI respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POE_API_KEY` | Your Poe API key (required) | None |
| `VCP_HEADLESS` | Run browser in headless mode | `true` |
| `VCP_TIMEOUT` | Browser timeout in milliseconds | `30000` |
| `VCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `VCP_CACHE_DIR` | Cache directory location | Platform default |

Example configuration:
```bash
export POE_API_KEY="your_poe_api_key_here"
export VCP_LOG_LEVEL="DEBUG"
export VCP_TIMEOUT="60000"
virginia-clemm-poe update --verbose
```

## Common Workflows

### Initial Setup Workflow

```bash
# 1. Install package
pip install virginia-clemm-poe

# 2. Set up browser
virginia-clemm-poe setup

# 3. Set API key
export POE_API_KEY="your_api_key_here"

# 4. Verify configuration
virginia-clemm-poe status

# 5. Fetch initial data
virginia-clemm-poe update

# 6. Search for models
virginia-clemm-poe search claude
```

### Daily Maintenance Workflow

```bash
# Check system health
virginia-clemm-poe status

# Update changed models only (fast)
virginia-clemm-poe update --pricing

# Search for new models
virginia-clemm-poe search "new"

# Check data coverage
virginia-clemm-poe list
```

### Research Workflow

```bash
# Update all data
virginia-clemm-poe update --all --force

# Find models by capability
virginia-clemm-poe search "vision" --show_bot_info
virginia-clemm-poe search "code" --show_bot_info

# Get comprehensive model list
virginia-clemm-poe list --with_pricing > models.txt

# Generate pricing comparison
virginia-clemm-poe search "claude" > claude_models.txt
virginia-clemm-poe search "gpt" > gpt_models.txt
```

### Troubleshooting Workflow

```bash
# Run comprehensive diagnostics
virginia-clemm-poe doctor

# Clear cache if issues persist
virginia-clemm-poe clear-cache

# Re-setup browser
virginia-clemm-poe setup --verbose

# Test with single model update
virginia-clemm-poe update --force --verbose

# Check cache performance
virginia-clemm-poe cache
```

## Output Formats and Styling

The CLI uses Rich for beautiful terminal output:

### Table Formatting
- **Borders**: Unicode box-drawing characters
- **Colors**: Syntax highlighting for different data types
- **Alignment**: Smart column alignment based on content
- **Wrapping**: Automatic text wrapping for long descriptions

### Status Indicators
- ✅ **Green checkmark**: Success/available
- ❌ **Red X**: Error/unavailable  
- ⚠️ **Yellow warning**: Caution/needs attention
- 🔄 **Blue info**: Processing/informational

### Progress Indicators
- Spinner animations for long operations
- Progress bars for batch updates
- Real-time status updates during scraping

## Automation and Scripting

### Exit Codes

Commands return standard exit codes for automation:
- `0`: Success
- `1`: Error or failure
- `2`: Invalid arguments

### JSON Output

Some commands support JSON output for programmatic use:

```bash
# Export model data as JSON (planned feature)
virginia-clemm-poe list --format json > models.json

# Search with JSON output (planned feature)
virginia-clemm-poe search claude --format json
```

### Batch Operations

```bash
#!/bin/bash
# batch_update.sh - Update specific model categories

models=("claude" "gpt" "gemini")

for model_type in "${models[@]}"; do
    echo "Updating $model_type models..."
    virginia-clemm-poe search "$model_type" 
    echo "Found models for $model_type"
done
```

### CI/CD Integration

```yaml
# .github/workflows/model-data.yml
name: Update Model Data

on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install package
        run: pip install virginia-clemm-poe
        
      - name: Setup browser
        run: virginia-clemm-poe setup
        
      - name: Update model data
        env:
          POE_API_KEY: ${{ secrets.POE_API_KEY }}
        run: virginia-clemm-poe update --all
        
      - name: Check status
        run: virginia-clemm-poe status
```

## Performance Tips

### Optimization Strategies

1. **Selective Updates**: Use `--pricing` or `--info` for faster updates
2. **Cache Management**: Monitor cache hit rates with `cache` command
3. **Incremental Updates**: Avoid `--force` unless necessary
4. **Network Optimization**: Increase timeout for slow connections

### Resource Management

```bash
# Monitor resource usage during updates
export VCP_LOG_LEVEL="DEBUG"
virginia-clemm-poe update --verbose

# Optimize for slow networks
export VCP_TIMEOUT="120000"  # 2 minutes
virginia-clemm-poe update

# Reduce memory usage
virginia-clemm-poe clear-cache --browser
virginia-clemm-poe update --pricing  # Only update pricing
```

### Error Recovery

```bash
# Automatic retry script
#!/bin/bash
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    virginia-clemm-poe update
    if [ $? -eq 0 ]; then
        echo "Update successful"
        exit 0
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Retry $RETRY_COUNT/$MAX_RETRIES"
    sleep 30
done

echo "Update failed after $MAX_RETRIES retries"
exit 1
```

## Configuration Files

### Default Locations

The CLI stores configuration in platform-appropriate locations:

**Linux/macOS:**
- Config: `~/.config/virginia-clemm-poe/config.json`
- Data: `~/.local/share/virginia-clemm-poe/`
- Cache: `~/.cache/virginia-clemm-poe/`
- Logs: `~/.local/share/virginia-clemm-poe/logs/`

**Windows:**
- Config: `%APPDATA%\virginia-clemm-poe\config.json`
- Data: `%LOCALAPPDATA%\virginia-clemm-poe\`
- Cache: `%LOCALAPPDATA%\virginia-clemm-poe\cache\`
- Logs: `%LOCALAPPDATA%\virginia-clemm-poe\logs\`

### Configuration Schema

```json
{
  "api_key": "your_poe_api_key",
  "browser": {
    "headless": true,
    "timeout": 30000,
    "debug_port": 9222,
    "user_agent": "custom_user_agent"
  },
  "cache": {
    "enabled": true,
    "max_age": 3600,
    "max_size": 1000
  },
  "logging": {
    "level": "INFO",
    "file": "~/.local/share/virginia-clemm-poe/logs/app.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

## Advanced Usage

### Custom Browser Configuration

```bash
# Use custom Chrome installation
export CHROME_PATH="/path/to/chrome"
virginia-clemm-poe setup

# Use custom user data directory
export VCP_USER_DATA_DIR="/path/to/userdata"
virginia-clemm-poe update
```

### Logging Configuration

```bash
# Enable debug logging
export VCP_LOG_LEVEL="DEBUG"
virginia-clemm-poe update --verbose 2>&1 | tee update.log

# Log to custom file
export VCP_LOG_FILE="/path/to/custom.log"
virginia-clemm-poe update
```

### Network Configuration

```bash
# Configure proxy
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
virginia-clemm-poe update

# Custom timeouts
export VCP_TIMEOUT="60000"  # 60 seconds
export VCP_NETWORK_TIMEOUT="30000"  # 30 seconds
virginia-clemm-poe update
```

This comprehensive CLI reference provides everything you need to effectively use Virginia Clemm Poe from the command line, whether for interactive exploration or automated workflows.