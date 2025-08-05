# Chapter 9: Troubleshooting and FAQ

## Quick Diagnostics

### Health Check Commands

Start with these commands to identify issues:

```bash
# Comprehensive system check
virginia-clemm-poe doctor

# Check current status
virginia-clemm-poe status

# Test basic functionality
virginia-clemm-poe search "test"

# Clear cache if issues persist
virginia-clemm-poe clear-cache
```

### Common Issue Indicators

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| "No model data found" | Missing or corrupted data file | `virginia-clemm-poe update` |
| "POE_API_KEY not set" | Missing API key | `export POE_API_KEY=your_key` |
| "Browser not available" | Chrome not installed | `virginia-clemm-poe setup` |
| "Cannot reach poe.com" | Network connectivity | Check internet/proxy settings |
| Slow updates | Resource constraints | Reduce concurrent limit |

## Installation Issues

### Python Version Problems

**Error**: `Package requires Python 3.12+`

**Solution**:
```bash
# Check current version
python --version

# Install Python 3.12+ using pyenv
curl https://pyenv.run | bash
pyenv install 3.12.0
pyenv global 3.12.0

# Or use system package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.12

# macOS:
brew install python@3.12
```

### Package Installation Failures

**Error**: `pip install virginia-clemm-poe fails`

**Common causes and solutions**:

1. **Outdated pip**:
```bash
pip install --upgrade pip
pip install virginia-clemm-poe
```

2. **Network issues**:
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org virginia-clemm-poe
```

3. **Permission errors**:
```bash
pip install --user virginia-clemm-poe
# or
python -m pip install virginia-clemm-poe
```

4. **Dependency conflicts**:
```bash
# Create clean environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install virginia-clemm-poe
```

### Browser Setup Issues

**Error**: `Failed to install browser dependencies`

**Solutions**:

1. **Manual Chrome installation**:
```bash
# Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update && sudo apt install google-chrome-stable

# macOS
brew install --cask google-chrome

# Windows
# Download from https://www.google.com/chrome/
```

2. **Check disk space**:
```bash
df -h  # Ensure at least 500MB free space
```

3. **Permissions**:
```bash
# Fix cache directory permissions
chmod -R 755 ~/.cache/virginia-clemm-poe/
```

## API and Authentication Issues

### API Key Problems

**Error**: `Invalid API key` or `Authentication failed`

**Solutions**:

1. **Verify API key format**:
```bash
# API key should be a long alphanumeric string
echo $POE_API_KEY | wc -c  # Should be 40+ characters
```

2. **Get new API key**:
   - Visit https://poe.com/api_key
   - Generate new key
   - Update environment variable

3. **Check key permissions**:
   - Ensure key has model listing permissions
   - Some keys may be rate-limited

### Network Connectivity Issues

**Error**: `Cannot reach poe.com` or `Connection timeout`

**Solutions**:

1. **Test connectivity**:
```bash
curl -I https://poe.com
curl -I https://api.poe.com/v2/models
```

2. **Proxy configuration**:
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
virginia-clemm-poe update
```

3. **Corporate firewall**:
   - Contact IT for API access approval
   - Use corporate proxy settings
   - Consider VPN if needed

4. **DNS issues**:
```bash
# Test DNS resolution
nslookup poe.com
# Try different DNS servers
export DNS_SERVER="8.8.8.8"
```

## Browser and Scraping Issues

### Browser Launch Failures

**Error**: `Failed to get browser` or `Chrome process exited`

**Solutions**:

1. **Check Chrome installation**:
```bash
# Test manual Chrome launch
google-chrome --version
chromium --version
```

2. **Port conflicts**:
```bash
# Check if port is in use
netstat -tulpn | grep :9222

# Use different port
virginia-clemm-poe update --debug_port 9223
```

3. **Insufficient resources**:
```bash
# Check system resources
free -m  # Memory
df -h    # Disk space

# Use low-resource mode
export VCP_MEMORY_LIMIT="256MB"
virginia-clemm-poe update --verbose
```

4. **Headless mode issues**:
```bash
# Try non-headless mode for debugging
export VCP_HEADLESS="false"
virginia-clemm-poe update --verbose
```

### Scraping Timeouts

**Error**: `Navigation timeout` or `Element not found`

**Solutions**:

1. **Increase timeouts**:
```bash
export VCP_TIMEOUT="60000"  # 60 seconds
virginia-clemm-poe update --verbose
```

2. **Reduce concurrency**:
```bash
export VCP_CONCURRENT_LIMIT="1"
virginia-clemm-poe update
```

3. **Network delays**:
```bash
export VCP_PAUSE_SECONDS="3.0"
virginia-clemm-poe update
```

4. **Debug specific models**:
```bash
# Enable verbose logging
virginia-clemm-poe update --verbose

# Check logs for failing models
tail -f ~/.local/share/virginia-clemm-poe/logs/app.log
```

### Anti-Bot Detection

**Error**: `Access denied` or `Captcha required`

**Solutions**:

1. **Rate limiting**:
```bash
# Slow down requests
export VCP_PAUSE_SECONDS="5.0"
export VCP_CONCURRENT_LIMIT="1"
virginia-clemm-poe update
```

2. **User agent rotation**:
```bash
export VCP_USER_AGENT="Mozilla/5.0 (compatible; virginia-clemm-poe/1.0)"
virginia-clemm-poe update
```

3. **Proxy rotation**:
```bash
# Use different proxy
export HTTP_PROXY="http://proxy2.example.com:8080"
virginia-clemm-poe update
```

4. **Wait and retry**:
```bash
# Wait before retrying
sleep 3600  # 1 hour
virginia-clemm-poe update --force
```

## Performance Issues

### Slow Updates

**Problem**: Updates take too long

**Solutions**:

1. **Increase concurrency** (if resources allow):
```bash
export VCP_CONCURRENT_LIMIT="10"
virginia-clemm-poe update
```

2. **Selective updates**:
```bash
# Update only pricing
virginia-clemm-poe update --pricing

# Skip force update
virginia-clemm-poe update  # Only updates missing data
```

3. **Cache optimization**:
```bash
# Clear old cache
virginia-clemm-poe clear-cache

# Optimize cache settings
export VCP_CACHE_TTL="7200"  # 2 hours
virginia-clemm-poe update
```

### Memory Issues

**Error**: `Out of memory` or system becomes unresponsive

**Solutions**:

1. **Reduce memory usage**:
```bash
export VCP_MEMORY_LIMIT="256MB"
export VCP_CONCURRENT_LIMIT="1"
virginia-clemm-poe update
```

2. **Enable garbage collection**:
```bash
export VCP_GC_THRESHOLD="0.7"
virginia-clemm-poe update --verbose
```

3. **Clear browser cache**:
```bash
virginia-clemm-poe clear-cache --browser
```

4. **Process batching**:
```bash
# Update in smaller batches
virginia-clemm-poe update --limit 50
```

### High CPU Usage

**Problem**: Process uses too much CPU

**Solutions**:

1. **Reduce browser instances**:
```bash
export VCP_MAX_BROWSERS="1"
virginia-clemm-poe update
```

2. **Add delays**:
```bash
export VCP_PAUSE_SECONDS="2.0"
virginia-clemm-poe update
```

3. **Lower priority**:
```bash
nice -n 10 virginia-clemm-poe update
```

## Data Issues

### Corrupted Data File

**Error**: `Invalid JSON` or `Validation error`

**Solutions**:

1. **Restore from backup**:
```bash
# Check for backups
ls ~/.local/share/virginia-clemm-poe/backups/

# Restore latest backup
cp ~/.local/share/virginia-clemm-poe/backups/poe_models_*.json \
   ~/.local/share/virginia-clemm-poe/poe_models.json
```

2. **Force fresh update**:
```bash
# Remove corrupted file
rm ~/.local/share/virginia-clemm-poe/poe_models.json

# Fetch fresh data
virginia-clemm-poe update --all
```

3. **Validate data manually**:
```python
import json
from virginia_clemm_poe.config import DATA_FILE_PATH

try:
    with open(DATA_FILE_PATH) as f:
        data = json.load(f)
    print("JSON is valid")
except json.JSONDecodeError as e:
    print(f"JSON error at line {e.lineno}: {e.msg}")
```

### Missing or Incomplete Data

**Problem**: Some models missing pricing or bot info

**Solutions**:

1. **Force update specific areas**:
```bash
# Update only missing pricing
virginia-clemm-poe update --pricing --force

# Update only missing bot info
virginia-clemm-poe update --info --force
```

2. **Check for errors**:
```bash
# Look for pricing errors in data
virginia-clemm-poe search "" --verbose | grep -i error
```

3. **Manual verification**:
```python
from virginia_clemm_poe import api

# Check data completeness
models = api.get_all_models()
need_update = api.get_models_needing_update()

print(f"Total models: {len(models)}")
print(f"Need update: {len(need_update)}")

# List models with errors
for model in models:
    if model.pricing_error:
        print(f"{model.id}: {model.pricing_error}")
```

## Environment-Specific Issues

### Docker Issues

**Problem**: Browser doesn't work in container

**Solutions**:

1. **Add required arguments**:
```dockerfile
ENV VCP_CHROME_ARGS="--no-sandbox,--disable-dev-shm-usage,--disable-gpu"
```

2. **Install dependencies**:
```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxss1 \
    xdg-utils
```

3. **Use privileged mode**:
```bash
docker run --privileged virginia-clemm-poe
```

### CI/CD Issues

**Problem**: Automated runs fail

**Solutions**:

1. **CI-specific configuration**:
```bash
export VCP_CI_MODE="true"
export VCP_HEADLESS="true"
export VCP_NON_INTERACTIVE="true"
virginia-clemm-poe update
```

2. **GitHub Actions example**:
```yaml
- name: Setup browser
  run: |
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    virginia-clemm-poe setup

- name: Update models
  env:
    POE_API_KEY: ${{ secrets.POE_API_KEY }}
    VCP_HEADLESS: true
  run: virginia-clemm-poe update --all
```

3. **Handle rate limits**:
```bash
# Longer delays in CI
export VCP_PAUSE_SECONDS="10.0"
export VCP_CONCURRENT_LIMIT="1"
```

### Windows-Specific Issues

**Problem**: Path or permission issues on Windows

**Solutions**:

1. **Use PowerShell**:
```powershell
$env:POE_API_KEY="your_key"
virginia-clemm-poe update
```

2. **Fix path issues**:
```powershell
# Use full paths
$env:VCP_DATA_FILE="C:\Users\YourName\AppData\Local\virginia-clemm-poe\poe_models.json"
```

3. **Antivirus exclusions**:
   - Add virginia-clemm-poe cache directory to exclusions
   - Temporarily disable real-time protection

## Debugging Techniques

### Enable Debug Logging

```bash
# Maximum verbosity
export VCP_LOG_LEVEL="DEBUG"
virginia-clemm-poe update --verbose 2>&1 | tee debug.log

# Structured logging
export VCP_STRUCTURED_LOGGING="true"
virginia-clemm-poe update --verbose
```

### Browser Debugging

```bash
# Save screenshots and page content
export VCP_SAVE_SCREENSHOTS="true"
export VCP_SAVE_PAGE_CONTENT="true"
virginia-clemm-poe update --verbose

# Check saved files
ls ~/.local/share/virginia-clemm-poe/debug/
```

### Network Debugging

```bash
# Monitor network traffic
export VCP_LOG_REQUESTS="true"
virginia-clemm-poe update --verbose

# Use proxy for inspection
export HTTP_PROXY="http://localhost:8080"  # Burp Suite or similar
virginia-clemm-poe update
```

### Memory Debugging

```python
from virginia_clemm_poe.utils.memory import enable_memory_profiling

# Enable memory profiling
enable_memory_profiling()

# Run operation
virginia-clemm-poe update --verbose

# Check memory report
cat ~/.local/share/virginia-clemm-poe/logs/memory_profile.log
```

## Getting Help

### Information to Gather

When seeking help, provide:

1. **System information**:
```bash
virginia-clemm-poe doctor > system_info.txt
python --version
uname -a  # Linux/macOS
systeminfo  # Windows
```

2. **Error logs**:
```bash
# Recent logs
tail -n 100 ~/.local/share/virginia-clemm-poe/logs/app.log

# Full debug run
virginia-clemm-poe update --verbose 2>&1 | tee full_debug.log
```

3. **Configuration**:
```bash
# Environment variables
env | grep VCP

# Configuration file
cat ~/.config/virginia-clemm-poe/config.json
```

### Support Channels

1. **GitHub Issues**: [Create detailed issue](https://github.com/terragonlabs/virginia-clemm-poe/issues)
2. **Documentation**: Check [official docs](https://terragonlabs.github.io/virginia-clemm-poe/)
3. **Community**: Join discussions and ask questions

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python version: 
- Virginia Clemm Poe version: 
- Browser: 

## Logs
```bash
# Paste relevant logs here
```

## Configuration
```json
// Paste relevant config here
```

## Additional Context
Any other relevant information
```

## Frequently Asked Questions

### General Questions

**Q: How often should I update the model data?**
A: Weekly updates are usually sufficient. More frequent updates may be needed when new models are released.

**Q: Can I use this without a Poe API key?**
A: No, the API key is required to fetch the initial model list from Poe.com.

**Q: Is it safe to run multiple update processes simultaneously?**
A: No, this can cause data corruption. Use the built-in concurrency controls instead.

**Q: Why are some models missing pricing data?**
A: Some models may have pricing errors, be in beta, or have updated page layouts that the scraper doesn't recognize yet.

### Technical Questions

**Q: How much data does the package store locally?**
A: Typically 2-10MB for the complete dataset, depending on the number of models.

**Q: Can I customize the scraping selectors?**
A: Yes, through configuration files or environment variables (see Chapter 8).

**Q: How do I integrate with my existing data pipeline?**
A: See the integration examples in Chapter 8 for database and API integrations.

**Q: What happens if Poe.com changes their website structure?**
A: The scraper may fail for new layouts. Update to the latest version or report the issue.

### Performance Questions

**Q: Why is the first update so slow?**
A: The first update scrapes all models. Subsequent updates only process changed models.

**Q: How can I speed up updates?**
A: Increase concurrency limits, use selective updates (--pricing or --info), and ensure good network connectivity.

**Q: Does the package cache data?**
A: Yes, it uses multiple cache layers for API responses, scraping results, and processed data.

This comprehensive troubleshooting guide should help resolve most issues you might encounter with Virginia Clemm Poe.