# Chapter 7: Browser Management and Web Scraping

## Overview

Virginia Clemm Poe uses sophisticated browser automation to scrape pricing and metadata from Poe.com that isn't available through the API. This chapter explains the browser management system, web scraping techniques, and how to troubleshoot automation issues.

## Browser Architecture

### PlaywrightAuthor Integration

The package uses the external [PlaywrightAuthor](https://github.com/sswam/playwrightauthor) package for robust browser management:

```python
from virginia_clemm_poe.browser_manager import BrowserManager

# Initialize browser manager
manager = BrowserManager(debug_port=9222, verbose=True)

# Get browser instance (handled automatically)
browser = await manager.get_browser()
```

**Key benefits of PlaywrightAuthor:**
- Automatic Chrome for Testing installation
- Robust browser lifecycle management
- DevTools Protocol connection handling
- Cross-platform compatibility

### Browser Pool Architecture

For efficient concurrent scraping, the package uses a browser pool system:

```python
from virginia_clemm_poe.browser_pool import BrowserPool, get_global_pool

# Get global browser pool instance
pool = get_global_pool()

# Use browser from pool
async with pool.get_browser() as browser:
    page = await browser.new_page()
    # ... scraping operations
```

**Pool Features:**
- **Connection Reuse**: Browsers stay alive between operations
- **Concurrent Scraping**: Multiple pages can run simultaneously
- **Resource Management**: Automatic cleanup and memory management
- **Error Recovery**: Handles browser crashes and restarts

## Scraping Pipeline

### Data Collection Process

1. **API Data Fetching**: Get basic model information from Poe API
2. **Browser Launch**: Start Chrome with DevTools Protocol
3. **Page Navigation**: Visit each model's Poe.com page
4. **Content Extraction**: Parse pricing tables and bot info cards
5. **Data Validation**: Validate scraped data with Pydantic models
6. **Storage**: Save enriched dataset to local JSON file

### Scraping Targets

#### Pricing Information

Extracted from pricing tables on model pages:

```html
<!-- Example pricing table structure -->
<table class="pricing-table">
  <tr>
    <td>Input (text)</td>
    <td>10 points/1k tokens</td>
  </tr>
  <tr>
    <td>Bot message</td>
    <td>5 points/message</td>
  </tr>
</table>
```

**Pricing Fields Scraped:**
- Input costs (text, image)
- Output costs (messages, images, video)
- Special rates (cache discounts, fine-tuning)
- Initial point costs from bot cards

#### Bot Information

Extracted from bot info cards and description sections:

```html
<!-- Example bot info structure -->
<div class="bot-info-card">
  <div class="creator">@anthropic</div>
  <div class="description">Claude is an AI assistant...</div>
  <div class="disclaimer">Powered by Claude-3 Sonnet</div>
</div>
```

**Bot Data Scraped:**
- Creator handles (e.g., "@anthropic", "@openai")
- Main descriptions and capabilities
- Additional disclaimers or details

## Browser Management Code

### BrowserManager Class

```python
from virginia_clemm_poe.browser_manager import BrowserManager

class BrowserManager:
    """Manages browser lifecycle using playwrightauthor."""
    
    def __init__(self, debug_port: int = 9222, verbose: bool = False):
        self.debug_port = debug_port
        self.verbose = verbose
        self._browser = None
    
    async def get_browser(self):
        """Get browser instance with automatic setup."""
        if self._browser is None or not self._browser.is_connected():
            from playwrightauthor import get_browser
            self._browser = await get_browser(
                headless=True,
                port=self.debug_port,
                verbose=self.verbose
            )
        return self._browser
    
    @staticmethod
    async def setup_chrome():
        """Ensure Chrome is installed."""
        from playwrightauthor.browser_manager import ensure_browser
        ensure_browser(verbose=True)
        return True
```

### Browser Pool Implementation

```python
from virginia_clemm_poe.browser_pool import BrowserPool

# Create browser pool
pool = BrowserPool(max_browsers=3, debug_port_start=9222)

# Use pool for concurrent operations
async def scrape_models_concurrently(model_ids):
    tasks = []
    
    for model_id in model_ids:
        task = scrape_single_model(pool, model_id)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

async def scrape_single_model(pool, model_id):
    async with pool.get_browser() as browser:
        page = await browser.new_page()
        try:
            # Navigate and scrape
            await page.goto(f"https://poe.com/{model_id}")
            pricing_data = await extract_pricing(page)
            return pricing_data
        finally:
            await page.close()
```

## Scraping Techniques

### Page Navigation

```python
async def navigate_to_model_page(page: Page, model_id: str):
    """Navigate to model page with error handling."""
    url = f"https://poe.com/{model_id}"
    
    try:
        # Navigate with timeout
        await page.goto(url, timeout=30000, wait_until="networkidle")
        
        # Wait for page to fully load
        await page.wait_for_load_state("domcontentloaded")
        
        # Handle potential modals or overlays
        await dismiss_modals(page)
        
    except PlaywrightTimeoutError:
        logger.warning(f"Timeout navigating to {url}")
        raise
    except Exception as e:
        logger.error(f"Navigation error for {model_id}: {e}")
        raise
```

### Modal and Dialog Handling

```python
async def dismiss_modals(page: Page):
    """Dismiss any modal dialogs that might block scraping."""
    
    # Common modal selectors
    modal_selectors = [
        "[data-testid='modal-close']",
        ".modal-close",
        "[aria-label='Close']",
        "button:has-text('Close')",
        "button:has-text('×')"
    ]
    
    for selector in modal_selectors:
        try:
            modal = await page.query_selector(selector)
            if modal and await modal.is_visible():
                await modal.click()
                await page.wait_for_timeout(1000)  # Wait for animation
                logger.debug(f"Dismissed modal: {selector}")
                break
        except Exception:
            continue  # Try next selector
```

### Data Extraction

#### Pricing Table Scraping

```python
async def extract_pricing_data(page: Page) -> dict[str, str]:
    """Extract pricing information from pricing tables."""
    pricing_data = {}
    
    # Look for pricing tables
    tables = await page.query_selector_all("table")
    
    for table in tables:
        rows = await table.query_selector_all("tr")
        
        for row in rows:
            cells = await row.query_selector_all("td")
            
            if len(cells) >= 2:
                # Get label and value
                label_element = cells[0]
                value_element = cells[1]
                
                label = await label_element.inner_text()
                value = await value_element.inner_text()
                
                # Clean and normalize
                label = label.strip()
                value = value.strip()
                
                if label and value:
                    pricing_data[label] = value
    
    return pricing_data
```

#### Bot Info Extraction

```python
async def extract_bot_info(page: Page) -> dict[str, str]:
    """Extract bot information from info cards."""
    bot_info = {}
    
    # Look for creator information
    creator_selectors = [
        "[data-testid='bot-creator']",
        ".bot-creator",
        "span:has-text('@')"
    ]
    
    for selector in creator_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                creator = await element.inner_text()
                if creator.startswith('@'):
                    bot_info['creator'] = creator
                    break
        except Exception:
            continue
    
    # Look for description
    description_selectors = [
        "[data-testid='bot-description']",
        ".bot-description",
        ".model-description"
    ]
    
    for selector in description_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                description = await element.inner_text()
                if description:
                    bot_info['description'] = description.strip()
                    break
        except Exception:
            continue
    
    return bot_info
```

### Error Handling and Resilience

```python
async def scrape_with_retry(page: Page, model_id: str, max_retries: int = 3):
    """Scrape model data with retry logic."""
    
    for attempt in range(max_retries):
        try:
            # Navigate to page
            await navigate_to_model_page(page, model_id)
            
            # Extract data
            pricing_data = await extract_pricing_data(page)
            bot_info = await extract_bot_info(page)
            
            return {
                'pricing': pricing_data,
                'bot_info': bot_info,
                'scraped_at': datetime.utcnow()
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Scraping attempt {attempt + 1} failed for {model_id}: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                logger.error(f"All scraping attempts failed for {model_id}: {e}")
                return {
                    'pricing': {},
                    'bot_info': {},
                    'error': str(e)
                }
```

## Performance Optimization

### Concurrent Scraping

```python
async def scrape_models_batch(model_ids: list[str], batch_size: int = 5):
    """Scrape models in controlled batches."""
    
    results = []
    pool = get_global_pool()
    
    # Process in batches to avoid overwhelming the server
    for i in range(0, len(model_ids), batch_size):
        batch = model_ids[i:i + batch_size]
        
        # Create tasks for batch
        tasks = [scrape_single_model(pool, model_id) for model_id in batch]
        
        # Execute batch with timeout
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Pause between batches
        if i + batch_size < len(model_ids):
            await asyncio.sleep(1)
    
    return results
```

### Memory Management

```python
from virginia_clemm_poe.utils.memory import MemoryManagedOperation

async def memory_efficient_scraping(model_ids: list[str]):
    """Scrape with memory monitoring and management."""
    
    async with MemoryManagedOperation("model_scraping") as mem_op:
        results = []
        
        for i, model_id in enumerate(model_ids):
            # Check memory usage
            if mem_op.should_gc():
                await mem_op.cleanup()
            
            # Scrape model
            result = await scrape_single_model_safe(model_id)
            results.append(result)
            
            # Log progress
            if i % 10 == 0:
                mem_op.log_progress(f"Scraped {i}/{len(model_ids)} models")
        
        return results
```

### Caching Strategy

```python
from virginia_clemm_poe.utils.cache import cached, get_scraping_cache

@cached(cache=get_scraping_cache(), ttl=3600, key_prefix="model_scrape")
async def scrape_model_cached(model_id: str) -> dict:
    """Scrape model with caching to avoid repeated requests."""
    pool = get_global_pool()
    
    async with pool.get_browser() as browser:
        page = await browser.new_page()
        try:
            return await scrape_model_data(page, model_id)
        finally:
            await page.close()
```

## Configuration and Customization

### Browser Settings

```python
# Environment variables for browser configuration
import os

browser_config = {
    'headless': os.getenv('VCP_HEADLESS', 'true').lower() == 'true',
    'timeout': int(os.getenv('VCP_TIMEOUT', '30000')),
    'debug_port': int(os.getenv('VCP_DEBUG_PORT', '9222')),
    'user_agent': os.getenv('VCP_USER_AGENT', None),
    'viewport': {
        'width': int(os.getenv('VCP_VIEWPORT_WIDTH', '1920')),
        'height': int(os.getenv('VCP_VIEWPORT_HEIGHT', '1080'))
    }
}
```

### Scraping Parameters

```python
# Timing configuration
TIMING_CONFIG = {
    'navigation_timeout': 30000,    # Page navigation timeout
    'load_timeout': 10000,         # Element load timeout
    'pause_between_requests': 1,    # Delay between requests
    'retry_delay': 2,              # Delay before retry
    'modal_wait': 1,               # Wait after modal dismiss
}

# Selector configuration
SELECTOR_CONFIG = {
    'pricing_table': [
        'table[data-testid="pricing"]',
        '.pricing-table',
        'table:has-text("Input")'
    ],
    'bot_creator': [
        '[data-testid="bot-creator"]',
        '.bot-creator',
        'span:has-text("@")'
    ],
    'bot_description': [
        '[data-testid="bot-description"]',
        '.bot-description',
        '.model-description'
    ]
}
```

## Troubleshooting Common Issues

### Browser Connection Problems

```python
async def diagnose_browser_issues():
    """Diagnose and report browser connectivity issues."""
    
    try:
        # Test browser installation
        from playwrightauthor.browser_manager import ensure_browser
        browser_path, data_dir = ensure_browser(verbose=True)
        print(f"✓ Browser found at: {browser_path}")
        
        # Test browser launch
        manager = BrowserManager(verbose=True)
        browser = await manager.get_browser()
        print(f"✓ Browser connected: {browser.is_connected()}")
        
        # Test page creation
        page = await browser.new_page()
        await page.goto("https://poe.com")
        print("✓ Page navigation successful")
        
        await page.close()
        await manager.close()
        
    except Exception as e:
        print(f"✗ Browser issue: {e}")
        return False
    
    return True
```

### Scraping Failures

```python
async def debug_scraping_failure(model_id: str):
    """Debug why scraping fails for a specific model."""
    
    pool = get_global_pool()
    
    async with pool.get_browser() as browser:
        page = await browser.new_page()
        
        try:
            # Enable request/response logging
            page.on("request", lambda req: print(f"→ {req.method} {req.url}"))
            page.on("response", lambda resp: print(f"← {resp.status} {resp.url}"))
            
            # Navigate with detailed logging
            url = f"https://poe.com/{model_id}"
            print(f"Navigating to: {url}")
            
            await page.goto(url, timeout=30000)
            print("Navigation complete")
            
            # Take screenshot for debugging
            await page.screenshot(path=f"debug_{model_id}.png")
            print(f"Screenshot saved: debug_{model_id}.png")
            
            # Check for pricing table
            pricing_tables = await page.query_selector_all("table")
            print(f"Found {len(pricing_tables)} tables")
            
            # Check for bot info
            creator_elements = await page.query_selector_all("span:has-text('@')")
            print(f"Found {len(creator_elements)} potential creator elements")
            
            # Get page content for manual inspection
            content = await page.content()
            with open(f"debug_{model_id}.html", "w") as f:
                f.write(content)
            print(f"Page content saved: debug_{model_id}.html")
            
        finally:
            await page.close()
```

### Performance Issues

```python
async def monitor_scraping_performance():
    """Monitor and report scraping performance metrics."""
    
    from virginia_clemm_poe.utils.timeout import with_timeout
    import time
    
    start_time = time.time()
    model_count = 0
    error_count = 0
    
    try:
        # Sample a few models for performance testing
        test_models = ["Claude-3-Opus", "GPT-4", "Claude-3-Sonnet"]
        
        for model_id in test_models:
            model_start = time.time()
            
            try:
                async with with_timeout(30.0):
                    await scrape_single_model_safe(model_id)
                
                model_time = time.time() - model_start
                print(f"✓ {model_id}: {model_time:.2f}s")
                model_count += 1
                
            except Exception as e:
                print(f"✗ {model_id}: {e}")
                error_count += 1
        
        total_time = time.time() - start_time
        success_rate = model_count / (model_count + error_count) * 100
        avg_time = total_time / len(test_models)
        
        print(f"\nPerformance Summary:")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average per model: {avg_time:.2f}s")
        print(f"Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"Performance monitoring failed: {e}")
```

## Best Practices

### Ethical Scraping

1. **Rate Limiting**: Respect server resources with delays between requests
2. **Error Handling**: Gracefully handle failures without overwhelming the server
3. **User Agent**: Use appropriate user agent strings
4. **Retry Logic**: Implement exponential backoff for retries

### Resource Management

1. **Browser Pooling**: Reuse browser instances to reduce overhead
2. **Memory Monitoring**: Track memory usage and trigger cleanup
3. **Connection Cleanup**: Always close pages and browsers properly
4. **Timeout Handling**: Set reasonable timeouts to prevent hangs

### Reliability

1. **Error Recovery**: Handle network issues and browser crashes
2. **Data Validation**: Validate scraped data before storage
3. **Fallback Strategies**: Have backup selectors for critical elements
4. **Logging**: Comprehensive logging for debugging and monitoring

This comprehensive guide to browser management and web scraping provides the foundation for understanding and extending Virginia Clemm Poe's data collection capabilities.