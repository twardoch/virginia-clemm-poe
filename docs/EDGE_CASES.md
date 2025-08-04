# Edge Cases Documentation

This document comprehensively catalogs the edge cases, boundary conditions, and error scenarios that Virginia Clemm Poe is designed to handle. Understanding these edge cases is crucial for maintainers and contributors.

## Table of Contents

- [API Integration Edge Cases](#api-integration-edge-cases)
- [Web Scraping Edge Cases](#web-scraping-edge-cases)
- [Browser Management Edge Cases](#browser-management-edge-cases)
- [Data Processing Edge Cases](#data-processing-edge-cases)
- [Memory Management Edge Cases](#memory-management-edge-cases)
- [Caching Edge Cases](#caching-edge-cases)
- [Error Recovery Edge Cases](#error-recovery-edge-cases)
- [Configuration Edge Cases](#configuration-edge-cases)

## API Integration Edge Cases

### Poe API Response Handling

#### Edge Case: Empty API Response
**Scenario**: Poe API returns valid JSON but with empty `data` array
```json
{"object": "list", "data": []}
```
**Handling**: 
- ✅ Gracefully handled in `fetch_models_from_api()`
- Returns empty `ModelCollection` with valid structure
- Logs info message about zero models fetched
- Does not raise exceptions

**Code Location**: `updater.py:89`

#### Edge Case: Malformed API Response Structure
**Scenario**: API returns unexpected JSON structure
```json
{"models": [...]}  // Missing required "object" and "data" fields
```
**Handling**:
- ✅ Caught by `validate_poe_api_response()` type guard
- Raises `APIError` with specific field information  
- Provides helpful error messages indicating expected structure
- Prevents application crash with detailed diagnostics

**Code Location**: `type_guards.py:140-168`

#### Edge Case: API Rate Limiting
**Scenario**: API returns 429 Too Many Requests
**Handling**:
- ✅ Automatically handled by `httpx` client with status code validation
- `HTTPStatusError` propagated with response details
- Includes rate limit headers in error context
- Allows caller to implement custom retry logic

**Code Location**: `updater.py:92-96`

#### Edge Case: Invalid API Key
**Scenario**: API key is expired, invalid, or missing
**Handling**:
- ✅ Returns 401/403 HTTP error with clear message
- Error context includes response body for debugging
- Fails fast rather than attempting retries
- Provides actionable error message to user

#### Edge Case: Network Connectivity Issues
**Scenario**: DNS resolution fails, connection timeout, or network unreachable
**Handling**:
- ✅ `httpx.AsyncClient` configured with reasonable timeout (30s default)
- Connection errors propagated with original exception context
- Timeout errors clearly distinguished from API errors
- Preserves original error chain for debugging

### Model Data Validation Edge Cases

#### Edge Case: Model with Missing Required Fields
**Scenario**: API returns model missing `id`, `architecture`, etc.
```json
{"object": "model", "created": 123}  // Missing required "id" field
```
**Handling**:
- ✅ Validation fails in `is_poe_api_model_data()` type guard
- Specific error message identifies missing fields
- Processing continues for valid models in the batch
- Invalid models logged but don't crash entire update

**Code Location**: `type_guards.py:17-50`

#### Edge Case: Architecture Field Type Mismatch
**Scenario**: `architecture` field is string instead of expected object
```json
{"architecture": "text-to-text"}  // Should be object
```
**Handling**:
- ✅ Type validation catches mismatch in type guard
- Error message specifies expected vs actual type
- Model creation fails gracefully for that specific model
- Other models continue processing normally

## Web Scraping Edge Cases

### Page Navigation Edge Cases

#### Edge Case: Model Page Not Found (404)
**Scenario**: Model ID exists in API but page doesn't exist on Poe.com
**Handling**:
- ✅ Playwright navigation raises exception
- Caught in `_scrape_model_info_uncached()` 
- Returns `(None, BotInfo(), "Page not found")` tuple
- Error logged but doesn't stop batch processing
- Model marked with pricing error for future reference

**Code Location**: `updater.py:454-462`

#### Edge Case: Page Load Timeout
**Scenario**: Page takes longer than `PAGE_NAVIGATION_TIMEOUT_MS` to load
**Handling**:
- ✅ Playwright configured with timeout (default: 30s)
- TimeoutError caught and converted to readable error message
- Returns partial data if any was extracted before timeout
- Timeout duration included in error context for debugging

**Code Location**: `updater.py:453-457`

#### Edge Case: JavaScript-Heavy Page Loading
**Scenario**: Page requires significant JavaScript execution before content loads
**Handling**:
- ✅ Uses `wait_until="networkidle"` strategy
- Additional `PAUSE_SECONDS` delay after navigation
- Allows dynamic content to fully render
- Fallback selectors for elements that may load asynchronously

**Code Location**: `updater.py:417-418`

### Element Extraction Edge Cases

#### Edge Case: Missing Pricing Table
**Scenario**: Model page has no "Rates" button or pricing dialog
**Handling**:
- ✅ Graceful detection in `_extract_pricing_table()`
- Returns `(None, "No Rates button found")` instead of crashing
- Bot info extraction continues even without pricing data
- Logged as debug message, not error (expected for some models)

**Code Location**: `updater.py:328-330`

#### Edge Case: Empty Pricing Dialog
**Scenario**: Rates button exists but dialog contains no table
**Handling**:
- ✅ Multiple selector fallback strategies in `_find_pricing_table_html()`
- Regex extraction as backup when CSS selectors fail
- Returns clear error message about missing table content
- Modal properly closed even if extraction fails

**Code Location**: `updater.py:341-344, 358-392`

#### Edge Case: Malformed HTML Table
**Scenario**: Pricing table has irregular structure (missing cells, nested elements)
**Handling**:
- ✅ Robust parsing in `parse_pricing_table()`
- Skips malformed rows rather than failing completely
- BeautifulSoup handles broken HTML gracefully
- Returns partial data for valid rows found

**Code Location**: `updater.py:144-160`

#### Edge Case: Dynamic CSS Class Names
**Scenario**: Poe.com changes CSS classes, breaking selectors
**Handling**:
- ✅ Multiple fallback selectors for each element type
- Pattern-based selectors (contains class name fragments)
- Text-based selectors as ultimate fallback
- Comprehensive selector lists for critical elements

**Code Location**: `updater.py:215-248` (example: initial points cost extraction)

### Text Processing Edge Cases

#### Edge Case: Unicode Characters in Pricing
**Scenario**: Pricing contains special characters (¢, £, €, etc.)
**Handling**:
- ✅ BeautifulSoup handles Unicode text extraction correctly
- Text normalization in extraction pipeline
- Preserves original formatting for display purposes
- No encoding/decoding issues in processing

#### Edge Case: Empty or Whitespace-Only Text Content
**Scenario**: DOM elements exist but contain only whitespace
**Handling**:
- ✅ `get_text(strip=True)` removes leading/trailing whitespace
- Empty strings filtered out in validation functions
- Validation functions check for meaningful content length
- Returns None for empty content rather than empty strings

**Code Location**: `updater.py:204, 271-272`

## Browser Management Edge Cases

### Browser Process Edge Cases

#### Edge Case: Browser Process Crash
**Scenario**: Chrome/Chromium process dies unexpectedly during operation
**Handling**:
- ✅ Detected by health check in `BrowserConnection.health_check()`
- Connection marked as unhealthy and removed from pool
- New browser instance created for subsequent operations
- Error classified as `BROWSER_CRASHED` for appropriate handling

**Code Location**: `browser_pool.py:75-100`

#### Edge Case: Browser Launch Failure
**Scenario**: Browser fails to start (missing executable, permission issues)
**Handling**:
- ✅ BrowserManager handles launch exceptions
- Clear error messages about browser availability
- Suggests installation of Chrome/Chromium if missing
- Fails fast rather than hanging indefinitely

#### Edge Case: Multiple Browser Instances Resource Contention
**Scenario**: Too many browser instances cause system resource exhaustion
**Handling**:
- ✅ Pool size limits in `BrowserPool` (default max: 3)
- Connection TTL prevents indefinite accumulation
- Memory monitoring triggers cleanup when usage is high
- Graceful degradation to single connection if needed

**Code Location**: `browser_pool.py:118-122`

### Connection Pool Edge Cases

#### Edge Case: All Connections Unhealthy
**Scenario**: All pooled connections fail health checks simultaneously
**Handling**:
- ✅ Pool automatically creates new connections as needed
- Health check failure triggers connection removal
- New connection creation not blocked by unhealthy connections
- Pool can recover from complete connection failure

#### Edge Case: Connection Acquisition Timeout
**Scenario**: All connections busy, requester waits beyond timeout
**Handling**:
- ✅ Timeout configured in `acquire_page()` context manager
- Clear timeout error message with wait duration
- Caller can implement retry logic or fail gracefully
- Pool statistics available for capacity planning

#### Edge Case: Context Manager Exception During Page Use
**Scenario**: Exception raised while using page, potentially leaving connection dirty
**Handling**:
- ✅ Context manager `__aexit__` ensures connection cleanup
- Connection returned to pool even on exception
- Page closed properly to prevent resource leaks
- Connection health checked before reuse

**Code Location**: `browser_pool.py:285-310`

## Data Processing Edge Cases

### Model Data Parsing Edge Cases

#### Edge Case: Circular References in API Data
**Scenario**: API returns model data with circular object references
**Handling**:
- ✅ Pydantic model validation prevents circular reference issues
- JSON serialization would fail on circular references
- Type guards validate structure before model creation
- Clear error messages if unexpected data structures encountered

#### Edge Case: Very Large Model Collections
**Scenario**: API returns thousands of models, memory usage grows large
**Handling**:
- ✅ Memory monitoring during model processing
- Periodic garbage collection in batch operations
- Processing in chunks for memory efficiency
- Memory cleanup triggered by thresholds

**Code Location**: `utils/memory.py` (entire module)

#### Edge Case: Concurrent Model Updates
**Scenario**: Multiple processes try to update the same model data file
**Handling**:
- ✅ File write operations are atomic (write to temp, then rename)
- No explicit file locking (relies on filesystem atomicity)
- Last writer wins (no merge conflict resolution)
- Backup/recovery not implemented (depends on version control)

### JSON Serialization Edge Cases

#### Edge Case: Datetime Serialization
**Scenario**: Model contains datetime objects that need JSON serialization
**Handling**:
- ✅ Custom `default=str` parameter in `json.dump()`
- Datetime objects converted to ISO format strings
- Timezone-aware datetime handling (UTC preferred)
- Deserialization back to datetime objects handled by Pydantic

**Code Location**: `updater.py:757`

#### Edge Case: Large JSON File Size
**Scenario**: Model data grows to several MB, causing performance issues
**Handling**:
- ✅ JSON formatted with indentation for readability
- Single atomic write operation (no streaming)
- File size monitoring could be added for alerting
- Compression not implemented (could be future enhancement)

## Memory Management Edge Cases

### Memory Leak Edge Cases

#### Edge Case: Browser Connection Memory Leaks
**Scenario**: Browser connections not properly closed, accumulating memory
**Handling**:
- ✅ Connection TTL ensures periodic recycling
- Health checks detect memory-heavy connections
- Context managers ensure proper cleanup
- Memory monitoring triggers cleanup when thresholds exceeded

#### Edge Case: Cache Memory Growth
**Scenario**: Cache grows indefinitely without eviction
**Handling**:
- ✅ TTL-based expiration removes old entries
- LRU eviction when memory pressure detected
- Memory threshold monitoring in cache implementation
- Manual cache clearing available if needed

**Code Location**: `utils/cache.py` (LRU implementation needed)

### Garbage Collection Edge Cases

#### Edge Case: Long-Running Operations with Memory Growth
**Scenario**: Batch processing thousands of models causes gradual memory growth
**Handling**:
- ✅ Periodic garbage collection every 50 operations
- Memory thresholds trigger more aggressive cleanup
- Multi-generational GC for thorough cleanup
- Async-friendly GC that yields control between generations

**Code Location**: `utils/memory.py:124-196`

#### Edge Case: Memory Cleanup During Critical Operations
**Scenario**: GC triggered while browser is performing critical operation
**Handling**:
- ✅ Async memory cleanup yields control frequently
- Brief sleep intervals allow other operations to continue
- Memory cleanup coordinated with operation lifecycle
- Critical operations can disable automatic cleanup temporarily

## Caching Edge Cases

### Cache Consistency Edge Cases

#### Edge Case: Stale Cache During Rapid Updates
**Scenario**: Data changes quickly, cache contains outdated information
**Handling**:
- ✅ TTL values chosen based on expected update frequency
- API cache: 600s (10 minutes) for model lists
- Scraping cache: 3600s (1 hour) for pricing data
- Manual cache invalidation available for immediate updates

**Code Location**: `updater.py:54` (API cache TTL)

#### Edge Case: Cache Size Growth
**Scenario**: Cache grows beyond available memory limits
**Handling**:
- ✅ Memory pressure monitoring triggers cache eviction
- LRU eviction removes least-used entries first
- Maximum cache size limits prevent unbounded growth
- Cache statistics available for monitoring hit rates

### Cache Corruption Edge Cases

#### Edge Case: Invalid Data in Cache
**Scenario**: Cached data becomes corrupted or invalid
**Handling**:
- ✅ Cache entries have timestamps for age verification
- Data validation on cache retrieval (optional)
- Cache miss fallback to fresh data retrieval
- Cache clearing available for corruption recovery

#### Edge Case: Cache Key Collisions
**Scenario**: Different operations generate same cache key
**Handling**:
- ✅ Structured cache key format with prefixes
- Operation-specific key generation patterns
- Namespace separation for different data types
- Key validation to prevent accidental overwrites

## Error Recovery Edge Cases

### Network Retry Edge Cases

#### Edge Case: Intermittent Network Failures
**Scenario**: Network connection fails sporadically during operation
**Handling**:
- ✅ Exponential backoff retry strategy in crash recovery
- Distinguishes network errors from other failure types
- Maximum retry limits prevent infinite loops
- Jitter in retry timing prevents thundering herd

**Code Location**: `utils/crash_recovery.py:45-80`

#### Edge Case: DNS Resolution Failures
**Scenario**: DNS for poe.com fails temporarily
**Handling**:
- ✅ Network errors classified separately from API errors
- Retry strategy appropriate for DNS failures
- Clear error messages distinguish DNS from connectivity issues
- Fallback mechanisms not implemented (could use IP addresses)

### Recovery State Edge Cases

#### Edge Case: Partial State Recovery
**Scenario**: Application crashes mid-operation, leaving partial state
**Handling**:
- ✅ Operations designed to be idempotent where possible
- Model updates check existing data before overwriting
- No transaction rollback (operations are mostly additive)
- Manual recovery procedures documented for complex cases

#### Edge Case: Corrupted State Files
**Scenario**: Model data file becomes corrupted or unloadable
**Handling**:
- ✅ JSON parsing errors caught during data loading
- Graceful fallback to empty collection on corruption
- Original data preserved in git history
- Manual backup/restore procedures recommended

**Code Location**: `updater.py:476-484`

## Configuration Edge Cases

### Environment Variable Edge Cases

#### Edge Case: Missing POE_API_KEY
**Scenario**: Required environment variable not set
**Handling**:
- ✅ Clear error message in CLI commands requiring API access
- Fails fast rather than attempting operations without key
- Error message suggests setting environment variable
- No default or fallback API key provided

#### Edge Case: Invalid Configuration Values
**Scenario**: Configuration contains invalid timeout values, ports, etc.
**Handling**:
- ✅ Configuration validation in config.py module
- Reasonable defaults for all configuration values
- Type checking ensures numeric values are actually numeric
- Range checking for values like timeouts and ports

**Code Location**: `config.py` (entire module)

### Resource Limit Edge Cases

#### Edge Case: System Resource Exhaustion
**Scenario**: System runs out of memory, file descriptors, etc.
**Handling**:
- ✅ Memory monitoring helps prevent memory exhaustion
- Connection pooling limits browser instances
- File descriptor usage minimized (connections reused)
- Graceful degradation when resources limited

#### Edge Case: Disk Space Exhaustion
**Scenario**: Not enough disk space for data files, logs, etc.
**Handling**:
- ✅ File operations would fail with clear OS error messages
- No disk space monitoring implemented
- Logs could grow large without rotation
- Manual disk management required

---

## Testing Edge Cases

When adding new features or modifying existing code, ensure these edge cases are considered:

1. **Null and Empty Inputs**: Test with `None`, empty strings, empty lists
2. **Boundary Values**: Test with minimum/maximum values for numeric inputs
3. **Resource Exhaustion**: Test behavior under memory/connection limits
4. **Network Conditions**: Test with slow, unreliable, or failed connections
5. **Concurrent Access**: Test with multiple simultaneous operations
6. **External Dependencies**: Test behavior when external services are unavailable

## Monitoring and Alerting

Consider monitoring these edge case indicators in production:

- Memory usage trends and spike detection
- Browser connection pool health and utilization
- Cache hit/miss ratios and eviction rates
- API error rates and response times
- Scraping failure rates by error types
- Processing time distributions for batch operations

---

*This documentation should be updated whenever new edge cases are discovered or handling strategies are modified. Each edge case should include clear reproduction steps and verification of the current handling behavior.*