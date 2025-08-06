# Poe Account Balance Feature

## Overview

This document describes the implementation of the Poe account balance checking feature for Virginia Clemm Poe. The feature allows users to authenticate with Poe, extract session cookies, and check their compute points balance.

## Implementation Summary

### 1. Core Components

#### PoeSessionManager (`src/virginia_clemm_poe/poe_session.py`)
- Manages Poe session cookies and authentication
- Stores cookies persistently in local data directory
- Provides methods for:
  - Extracting cookies from browser sessions
  - Checking account balance via internal Poe API
  - Integration with poe-api-wrapper (if installed)

Key methods:
- `extract_cookies_from_browser()`: Extract cookies from browser context
- `login_with_browser()`: Interactive browser login
- `extract_from_existing_playwright_session()`: Extract from PlaywrightAuthor session
- `get_account_balance()`: Retrieve compute points and subscription info
- `has_valid_cookies()`: Check if authenticated
- `clear_cookies()`: Logout functionality

#### API Module Updates (`src/virginia_clemm_poe/api.py`)
Added public API functions:
- `get_account_balance()`: Get compute points balance
- `login_to_poe()`: Interactive browser login
- `extract_poe_cookies()`: Extract cookies from existing browser session
- `has_valid_poe_session()`: Check authentication status
- `clear_poe_session()`: Clear stored cookies

#### CLI Commands (`src/virginia_clemm_poe/__main__.py`)
New commands added:
- `virginia-clemm-poe balance [--login]`: Check account balance
- `virginia-clemm-poe login`: Interactive Poe login
- `virginia-clemm-poe logout`: Clear session cookies

### 2. Authentication Flow

1. **Initial Login**:
   - User runs `virginia-clemm-poe login`
   - Browser window opens to Poe.com login page
   - User manually logs in (supports 2FA)
   - Cookies are extracted and stored locally

2. **Cookie Storage**:
   - Essential cookies (p-b, p-lat, m-b, cf_clearance) are extracted
   - Stored in `~/Library/Application Support/virginia-clemm-poe/cookies/poe_cookies.json`
   - Cookies persist between sessions

3. **Balance Checking**:
   - Uses stored cookies to query internal Poe API endpoint
   - Endpoint: `https://www.quora.com/poe_api/settings`
   - Returns compute points, subscription status, daily points

### 3. Integration with PlaywrightAuthor

The implementation is designed to work seamlessly with PlaywrightAuthor:
- Can extract cookies from existing PlaywrightAuthor browser sessions
- Uses the same browser pool for login operations
- Compatible with CDP (Chrome DevTools Protocol) sessions

### 4. Features

- **Persistent Authentication**: Cookies stored locally, no need to re-login each time
- **Balance Information**: Shows compute points, daily points, subscription status
- **Session Management**: Login, logout, and session validation
- **Error Handling**: Graceful handling of expired cookies and authentication failures
- **Optional poe-api-wrapper Integration**: Can use poe-api-wrapper for enhanced functionality if installed

## Usage Examples

### Check Balance
```bash
# If already logged in
virginia-clemm-poe balance

# Login and check balance
virginia-clemm-poe balance --login
```

### Login/Logout
```bash
# Interactive login
virginia-clemm-poe login

# Clear session
virginia-clemm-poe logout
```

### Python API
```python
import asyncio
from virginia_clemm_poe import api

async def check_balance():
    # Check if logged in
    if not api.has_valid_poe_session():
        # Login interactively
        await api.login_to_poe()
    
    # Get balance
    balance = await api.get_account_balance()
    print(f"Compute points: {balance['compute_points_available']:,}")

asyncio.run(check_balance())
```

## Technical Details

### Cookie Extraction
The implementation extracts the following essential cookies:
- `p-b`: Primary session token
- `p-lat`: Session latitude token  
- `m-b`: Message token
- `__cf_bm`: Cloudflare bot management
- `cf_clearance`: Cloudflare clearance

### API Endpoints Used
- Login: `https://poe.com/login`
- Settings/Balance: `https://www.quora.com/poe_api/settings`

### Data Storage
- Cookies: `{data_dir}/cookies/poe_cookies.json`
- Data directory varies by platform:
  - macOS: `~/Library/Application Support/virginia-clemm-poe/`
  - Linux: `~/.local/share/virginia-clemm-poe/`
  - Windows: `%LOCALAPPDATA%\virginia-clemm-poe\`

## Future Enhancements

1. **Automatic Token Refresh**: Detect expired cookies and prompt for re-login
2. **Enhanced poe-api-wrapper Integration**: Use for model details and advanced features
3. **Multi-Account Support**: Allow switching between multiple Poe accounts
4. **Balance History Tracking**: Store and display balance history over time
5. **Usage Analytics**: Track compute point usage patterns

## Testing

A test script is provided at `test_balance.py` to verify the implementation:

```bash
python test_balance.py
```

This tests:
- Session manager functionality
- Cookie storage and retrieval
- Balance checking (if authenticated)
- CLI command availability

## Dependencies

The feature uses:
- `httpx`: For API requests with cookies
- `playwright`: For browser automation
- `loguru`: For logging
- `poe-api-wrapper` (optional): For enhanced functionality

## Security Considerations

- Cookies are stored locally in the user's data directory
- No credentials are stored, only session cookies
- Users must manually authenticate through the browser
- Cookies can be cleared with the logout command