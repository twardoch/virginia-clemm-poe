# Complex Algorithms Documentation

This document provides detailed explanations of the complex algorithms used in Virginia Clemm Poe, including their design rationale, implementation details, and performance characteristics.

## Table of Contents

- [Browser Connection Pooling Algorithm](#browser-connection-pooling-algorithm)
- [Memory Management Algorithm](#memory-management-algorithm)
- [Crash Detection and Recovery Algorithm](#crash-detection-and-recovery-algorithm)
- [Adaptive Caching Algorithm](#adaptive-caching-algorithm)
- [HTML Pricing Table Parsing Algorithm](#html-pricing-table-parsing-algorithm)

## Browser Connection Pooling Algorithm

### Overview

The browser connection pooling algorithm (`browser_pool.py`) implements sophisticated resource management for browser instances to optimize performance during bulk web scraping operations.

### Algorithm Design

**Problem**: Creating and destroying browser instances for each scraping operation is expensive (2-5 seconds per instance), but keeping browsers open indefinitely leads to memory leaks and resource exhaustion.

**Solution**: A pooled connection system with health monitoring, connection reuse, and automatic cleanup.

### Core Algorithm

```
ALGORITHM: Browser Connection Pool Management

INPUT: 
  - max_size: Maximum pool connections (default: 3)
  - connection_ttl: Connection time-to-live (default: 300s)
  - health_check_interval: Health check frequency (default: 60s)

DATA STRUCTURES:
  - available_connections: Queue[BrowserConnection] (idle connections)
  - active_connections: Set[BrowserConnection] (in-use connections)
  - connection_stats: Dict[str, Any] (performance metrics)

MAIN POOL OPERATIONS:

1. CONNECTION ACQUISITION:
   ```
   FUNCTION acquire_connection():
     IF available_connections.empty():
       IF total_connections < max_size:
         connection = create_new_connection()
         return connection
       ELSE:
         WAIT for connection to become available (timeout: 30s)
     
     connection = available_connections.dequeue()
     
     IF connection.age_seconds() > connection_ttl:
       close_connection(connection)
       GOTO acquire_connection()  // Recursive retry
     
     IF NOT await connection.health_check():
       close_connection(connection)
       GOTO acquire_connection()  // Recursive retry
       
     active_connections.add(connection)
     connection.mark_used()
     return connection
   ```

2. CONNECTION RELEASE:
   ```
   FUNCTION release_connection(connection):
     active_connections.remove(connection)
     
     IF connection.is_healthy AND connection.age_seconds() < connection_ttl:
       available_connections.enqueue(connection)
     ELSE:
       close_connection(connection)
   ```

3. HEALTH MONITORING:
   ```
   FUNCTION health_check_cycle():
     FOR EACH connection IN available_connections:
       IF NOT await connection.health_check():
         remove_and_close(connection)
       
     FOR EACH connection IN active_connections:
       IF connection.idle_seconds() > max_idle_time:
         log_warning("Long-running connection detected")
   ```
```

### Connection Lifecycle States

1. **CREATING**: Browser instance being launched (2-5 seconds)
2. **AVAILABLE**: Ready for use, sitting in available queue
3. **ACTIVE**: Currently being used for scraping operations
4. **HEALTH_CHECK**: Being validated for continued use
5. **CLOSING**: Being gracefully shut down
6. **FAILED**: Marked for removal due to health check failure

### Health Check Algorithm

The health check algorithm uses a multi-stage validation approach:

```
ALGORITHM: Browser Connection Health Check

FUNCTION health_check(connection):
  1. LIGHTWEIGHT_TEST:
     TRY:
       page = connection.context.new_page() WITH timeout=5s
       page.close()
       return HEALTHY
     CATCH TimeoutError:
       return UNHEALTHY (reason: "timeout")
     CATCH BrowserDisconnectedError:
       return UNHEALTHY (reason: "browser_crashed")
     CATCH Exception as e:
       crash_type = classify_crash(e)
       return UNHEALTHY (reason: crash_type)

  2. CRASH_CLASSIFICATION:
     IF "Target page, context or browser has been closed" IN error:
       return BROWSER_CRASHED
     IF "Connection closed" IN error:  
       return CONNECTION_LOST
     IF "timeout" IN error.lower():
       return TIMEOUT
     ELSE:
       return GENERIC_ERROR
```

### Performance Characteristics

- **Connection Creation**: O(1) amortized, O(n) worst case (when creating new browser)
- **Connection Acquisition**: O(1) average case, O(log n) with health checks
- **Memory Usage**: Linear with pool size (~50-100MB per browser instance)
- **Scalability**: Designed for 1-10 concurrent connections

### Edge Cases Handled

1. **Browser Process Death**: Detected via health checks, connections auto-removed
2. **Memory Leaks**: Connections have TTL and are periodically recycled
3. **Network Failures**: Timeout handling prevents indefinite blocking
4. **Race Conditions**: Thread-safe operations with asyncio locks
5. **Resource Exhaustion**: Pool size limits prevent runaway resource usage

## Memory Management Algorithm

### Overview

The memory management algorithm (`memory.py`) implements proactive memory monitoring and cleanup to maintain steady-state memory usage below 200MB during long-running operations.

### Core Algorithm

```
ALGORITHM: Adaptive Memory Management

CONSTANTS:
  - MEMORY_WARNING_THRESHOLD = 150MB
  - MEMORY_CRITICAL_THRESHOLD = 200MB  
  - MEMORY_CLEANUP_THRESHOLD = 180MB
  - GC_COLLECT_THRESHOLD_OPERATIONS = 50 operations
  - MONITORING_INTERVAL = 30 seconds

FUNCTION memory_management_loop():
  WHILE application_running:
    current_memory = get_memory_usage()
    
    IF should_run_cleanup():
      cleanup_result = perform_memory_cleanup()
      log_cleanup_metrics(cleanup_result)
    
    IF current_memory > MEMORY_CRITICAL_THRESHOLD:
      log_error("Critical memory usage detected")
      force_garbage_collection()
    
    sleep(MONITORING_INTERVAL)

FUNCTION should_run_cleanup():
  // Multi-criteria decision logic
  return (
    current_memory > MEMORY_CLEANUP_THRESHOLD OR
    operation_count >= GC_COLLECT_THRESHOLD_OPERATIONS OR  
    time_since_last_cleanup > MONITORING_INTERVAL
  )

FUNCTION perform_memory_cleanup():
  memory_before = get_memory_usage()
  
  // Multi-generational garbage collection
  objects_collected = 0
  FOR generation IN [0, 1, 2]:
    objects_collected += gc.collect(generation)
  
  // Allow async tasks to yield
  await asyncio.sleep(0.01)
  
  memory_after = get_memory_usage()
  memory_freed = memory_before - memory_after
  
  return CleanupResult(
    memory_freed=memory_freed,
    objects_collected=objects_collected,
    cleanup_time=elapsed_time
  )
```

### Memory Monitoring Strategy

The algorithm uses a three-tier monitoring approach:

1. **Proactive Monitoring**: Continuous background memory tracking
2. **Threshold-Based Cleanup**: Automatic cleanup when thresholds are exceeded  
3. **Emergency Intervention**: Forced cleanup for critical memory situations

### Garbage Collection Strategy

```
ALGORITHM: Multi-Generational Garbage Collection

FUNCTION force_garbage_collection():
  // Collect in reverse generation order for maximum effectiveness
  FOR generation IN [2, 1, 0]:
    collected = gc.collect(generation)
    log_debug(f"Generation {generation}: {collected} objects collected")
    
    // Brief pause to allow other async tasks to run
    await asyncio.sleep(0.001)
```

### Performance Impact Mitigation

1. **Async-Friendly**: Uses `asyncio.sleep()` to yield control during cleanup
2. **Incremental Collection**: Processes generations separately to reduce pause times
3. **Adaptive Frequency**: Adjusts cleanup frequency based on memory pressure
4. **Selective Monitoring**: Only monitors during memory-intensive operations

## Crash Detection and Recovery Algorithm

### Overview

The crash detection algorithm (`crash_recovery.py`) implements intelligent error classification and recovery strategies for browser automation failures.

### Crash Classification Algorithm

```
ALGORITHM: Intelligent Crash Detection

FUNCTION detect_crash_type(exception, operation_context):
  error_message = str(exception).lower()
  
  // Pattern-based classification using error signatures
  MATCH error_message:
    CASE CONTAINS "target page, context or browser has been closed":
      return BROWSER_CRASHED
    CASE CONTAINS "connection closed" OR "websocket":
      return CONNECTION_LOST  
    CASE CONTAINS "timeout" OR "timed out":
      return TIMEOUT
    CASE CONTAINS "network error" OR "net::":
      return NETWORK_ERROR
    CASE isinstance(exception, TimeoutError):
      return TIMEOUT
    CASE isinstance(exception, ConnectionError):
      return CONNECTION_LOST
    DEFAULT:
      return GENERIC_ERROR

FUNCTION classify_severity(crash_type):
  MATCH crash_type:
    CASE BROWSER_CRASHED, CONNECTION_LOST:
      return CRITICAL  // Requires browser restart
    CASE TIMEOUT, NETWORK_ERROR:
      return RECOVERABLE  // Can retry with backoff
    CASE GENERIC_ERROR:
      return UNKNOWN  // Needs investigation
```

### Recovery Strategy Algorithm

```
ALGORITHM: Exponential Backoff with Jitter

FUNCTION recover_with_backoff(operation, max_attempts=3):
  FOR attempt IN range(1, max_attempts + 1):
    TRY:
      result = await operation()
      return SUCCESS(result)
    
    CATCH Exception as e:
      crash_type = detect_crash_type(e, operation)
      severity = classify_severity(crash_type)
      
      IF attempt == max_attempts:
        return FAILURE(e, attempts=attempt)
      
      IF severity == CRITICAL:
        // Immediate escalation for critical failures
        await cleanup_resources()
        return FAILURE(e, attempts=attempt)
      
      // Calculate backoff with exponential growth and jitter
      base_delay = 2 ** attempt  // 2, 4, 8 seconds
      jitter = random.uniform(0.1, 0.3) * base_delay
      delay = base_delay + jitter
      
      log_retry_attempt(attempt, delay, crash_type)
      await asyncio.sleep(delay)
  
  return FAILURE("Max attempts exceeded")
```

### Recovery Decision Matrix

| Crash Type | Severity | Action | Retry Strategy |
|-----------|----------|--------|----------------|
| BROWSER_CRASHED | Critical | Restart browser | No retry |
| CONNECTION_LOST | Critical | Recreate connection | No retry |
| TIMEOUT | Recoverable | Exponential backoff | 3 attempts |
| NETWORK_ERROR | Recoverable | Linear backoff | 3 attempts |
| GENERIC_ERROR | Unknown | Conservative backoff | 2 attempts |

## Adaptive Caching Algorithm

### Overview

The caching algorithm (`cache.py`) implements TTL-based caching with memory pressure awareness and hit rate optimization.

### Cache Eviction Algorithm

```
ALGORITHM: LRU with TTL and Memory Pressure

DATA STRUCTURES:
  - cache_entries: Dict[str, CacheEntry]
  - access_order: OrderedDict[str, timestamp]  // LRU tracking
  - ttl_index: SortedDict[timestamp, List[str]]  // TTL expiration index

FUNCTION cache_get(key):
  IF key NOT IN cache_entries:
    return CACHE_MISS
  
  entry = cache_entries[key]
  
  IF current_time() > entry.expires_at:
    remove_expired_entry(key)
    return CACHE_MISS
  
  // Update LRU order
  access_order.move_to_end(key)
  entry.hit_count += 1
  
  return CACHE_HIT(entry.data)

FUNCTION cache_set(key, value, ttl):
  // Check memory pressure before adding
  IF get_memory_usage() > CACHE_MEMORY_THRESHOLD:
    evict_lru_entries(count=10)
  
  expires_at = current_time() + ttl
  entry = CacheEntry(value, expires_at, hit_count=0)
  
  cache_entries[key] = entry
  access_order[key] = current_time()
  ttl_index[expires_at].append(key)

FUNCTION evict_lru_entries(count):
  // Remove least recently used entries
  FOR i IN range(count):
    IF access_order.empty():
      break
    
    lru_key = access_order.popitem(last=False)[0]
    remove_cache_entry(lru_key)
```

### TTL Management

```
ALGORITHM: Efficient TTL Expiration

FUNCTION cleanup_expired_entries():
  current_time = current_time()
  expired_keys = []
  
  // Use sorted TTL index for efficient expiration
  FOR expire_time, keys IN ttl_index:
    IF expire_time > current_time:
      break  // All remaining entries are still valid
    
    expired_keys.extend(keys)
    ttl_index.pop(expire_time)
  
  FOR key IN expired_keys:
    remove_cache_entry(key)
  
  return len(expired_keys)
```

## HTML Pricing Table Parsing Algorithm

### Overview

The pricing table parsing algorithm (`updater.py`) implements robust HTML table parsing with multi-format support and error recovery.

### Parsing State Machine

```
ALGORITHM: HTML Table Parsing State Machine

STATES: 
  - SEEKING_TABLE: Looking for table element
  - PROCESSING_HEADERS: Processing table headers (th elements)
  - PROCESSING_DATA: Processing data rows (td elements)
  - EXTRACTING_VALUES: Extracting cell content
  - COMPLETE: Parsing finished

FUNCTION parse_pricing_table(html):
  soup = BeautifulSoup(html, "html.parser")
  table = soup.find("table")
  
  IF table IS None:
    RAISE ValueError("No table found")
  
  pricing_data = {}
  state = PROCESSING_DATA
  
  FOR row IN table.find_all("tr"):
    cells = row.find_all(["th", "td"])
    
    // Skip header-only rows  
    IF all(cell.name == "th" for cell in cells):
      state = PROCESSING_HEADERS
      CONTINUE
    
    // Process data rows
    IF state == PROCESSING_DATA:
      processed_row = process_table_row(cells)
      IF processed_row:
        key, values = processed_row
        pricing_data[key] = format_cell_values(values)
  
  return pricing_data

FUNCTION process_table_row(cells):
  IF len(cells) == 0:
    return None
  
  // Extract text content with normalization
  texts = []
  FOR cell IN cells:
    text = cell.get_text(strip=True)
    normalized_text = normalize_pricing_text(text)
    texts.append(normalized_text)
  
  key = texts[0]  // First cell is the key
  values = texts[1:]  // Remaining cells are values
  
  return key, values

FUNCTION format_cell_values(values):
  IF len(values) == 0:
    return None
  ELIF len(values) == 1:
    return values[0]
  ELSE:
    return values  // Return array for multi-value cells
```

### Text Normalization Pipeline

```
ALGORITHM: Pricing Text Normalization

FUNCTION normalize_pricing_text(raw_text):
  // Multi-stage normalization pipeline
  
  1. WHITESPACE_NORMALIZATION:
     text = re.sub(r'\s+', ' ', raw_text.strip())
  
  2. UNICODE_NORMALIZATION:
     text = unicodedata.normalize('NFKC', text)
  
  3. CURRENCY_STANDARDIZATION:
     text = standardize_currency_symbols(text)
  
  4. NUMERIC_FORMATTING:
     text = normalize_numeric_values(text)
  
  return text

FUNCTION standardize_currency_symbols(text):
  replacements = {
    '¢': 'cents',
    '£': 'GBP',
    '€': 'EUR',
    '¥': 'JPY'
  }
  
  FOR symbol, replacement IN replacements:
    text = text.replace(symbol, replacement)
  
  return text
```

### Error Recovery Strategies

1. **Malformed HTML**: Use BeautifulSoup's lenient parsing
2. **Missing Tables**: Graceful fallback with clear error messages
3. **Empty Cells**: Handle None values appropriately
4. **Nested Elements**: Recursive text extraction
5. **Encoding Issues**: Unicode normalization and error handling

---

*This documentation is maintained as part of the Virginia Clemm Poe project's code quality standards. For questions or updates, please refer to the contribution guidelines in CONTRIBUTING.md.*