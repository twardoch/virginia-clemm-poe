# Poe Account Balance Feature

## Overview

This document describes the implementation of the Poe account balance checking feature for Virginia Clemm Poe. The feature allows users to authenticate with Poe, extract session cookies, and check their compute points balance.

## Implementation Summary

### 1. Core Components

#### PoeSessionManager (`src/virginia_clemm_poe/poe_session.py`)
Manages Poe session cookies and authentication. Stores cookies persistently in the local data directory.

Key methods:
- `extract_cookies_from_browser()`: Extract cookies from browser sessions
- `login_with_browser()`: Interactive browser login
- `extract_from_existing_playwright_session()`: Extract from PlaywrightAuthor sessions
- `get_account_balance()`: Retrieve compute points and subscription info
- `has_valid_cookies()`: Check authentication status
- `clear_cookies()`: Logout functionality

#### API Module Updates (`src/virginia_clemm_poe/api.py`)
Added public API functions:
- `get_account_balance()`: Get compute points balance
- `login_to_poe()`: Interactive browser login
- `extract_poe_cookies()`: Extract cookies from existing browser sessions
- `has_valid_poe_session()`: Check authentication status
- `clear_poe_session()`: Clear stored cookies

#### CLI Commands (`src/virginia_clemm_poe/__main__.py`)
New commands:
- `virginia-clemm-poe balance [--login]`: Check account balance
- `virginia-clemm-poe login`: Interactive Poe login
- `virginia-clemm-poe logout`: Clear session cookies

### 2. Authentication Flow

1. **Initial Login**:
   - User runs `virginia-clemm-poe login`
   - Browser opens to Poe.com login page
   - User logs in manually (2FA supported)
   - Cookies are extracted and stored locally

2. **Cookie Storage**:
   - Extracts essential cookies: p-b, p-lat, m-b, cf_clearance
   - Stores in `~/Library/Application Support/virginia-clemm-poe/cookies/poe_cookies.json`
   - Cookies persist between sessions

3. **Balance Checking**:
   - Uses stored cookies to query Poe's internal API
   - Endpoint: `https://www.quora.com/poe_api/settings`
   - Returns compute points, subscription status, daily points

### 3. PlaywrightAuthor Integration

Works with PlaywrightAuthor:
- Extracts cookies from existing PlaywrightAuthor sessions
- Uses the same browser pool for login operations
- Compatible with CDP sessions

### 4. Features

- **Persistent Authentication**: No need to re-login each time
- **Balance Information**: Compute points, daily points, subscription status
- **Session Management**: Login, logout, and validation
- **Error Handling**: Handles expired cookies and authentication failures
- **Optional Integration**: Works with poe-api-wrapper if installed

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
        await api.login_to_poe()
    
    # Get balance
    balance = await api.get_account_balance()
    print(f"Compute points: {balance['compute_points_available']:,}")

asyncio.run(check_balance())
```

## Technical Details

### Cookie Extraction
Extracts essential cookies:
- `p-b`: Primary session token
- `p-lat`: Session latitude token  
- `m-b`: Message token
- `__cf_bm`: Cloudflare bot management
- `cf_clearance`: Cloudflare clearance

### API Endpoints
- Login: `https://poe.com/login`
- Settings/Balance: `https://www.quora.com/poe_api/settings`

### Data Storage
- Cookies: `{data_dir}/cookies/poe_cookies.json`
- Data directory by platform:
  - macOS: `~/Library/Application Support/virginia-clemm-poe/`
  - Linux: `~/.local/share/virginia-clemm-poe/`
  - Windows: `%LOCALAPPDATA%\virginia-clemm-poe\`

## Future Enhancements

1. **Automatic Token Refresh**: Detect expired cookies and prompt for re-login
2. **Enhanced Integration**: Use poe-api-wrapper for model details
3. **Multi-Account Support**: Switch between multiple Poe accounts
4. **Balance History**: Store and display balance history
5. **Usage Analytics**: Track compute point usage patterns

## Testing

Test script at `test_balance.py`:

```bash
python test_balance.py
```

Tests:
- Session manager functionality
- Cookie storage and retrieval
- Balance checking (if authenticated)
- CLI command availability

## Dependencies

- `httpx`: API requests with cookies
- `playwright`: Browser automation
- `loguru`: Logging
- `poe-api-wrapper` (optional): Enhanced functionality

## Security Considerations

- Cookies stored locally in user's data directory
- No credentials stored, only session cookies
- Manual browser authentication required
- Logout command clears cookies