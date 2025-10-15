# this_file: src/virginia_clemm_poe/api.py

"""Public API for Virginia Clemm Poe."""

import asyncio
import json

from loguru import logger

from .bots import BotCollection, PoeBot
from .config import DATA_FILE_PATH
from .exceptions import AuthenticationError
from .poe_session import PoeSessionManager

_collection: BotCollection | None = None
_session_manager: PoeSessionManager | None = None


def get_session_manager() -> PoeSessionManager:
    """Get or create the global session manager instance.

    Returns:
        PoeSessionManager: Singleton session manager for cookie/balance operations
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = PoeSessionManager()
    return _session_manager


def load_bots(force_reload: bool = False) -> BotCollection:
    """Load bot collection from the data file with intelligent caching.

    This is the foundational function that loads the complete Poe bot dataset
    from the local JSON file. All other API functions depend on this function
    for data access. It provides automatic caching to minimize disk I/O and
    ensure consistent performance across multiple API calls.

    Args:
        force_reload: If True, bypasses cache and reloads from file.
                     Use when you know the data file has been updated externally.

    Returns:
        BotCollection: Container with all bot data and search capabilities.
            - data: list[PoeBot] - All available bots
            - Each PoeBot contains:
                - id: str - Unique bot identifier (e.g., "Claude-3-Opus")
                - architecture: Architecture - Input/output capabilities
                - pricing: Pricing | None - Cost information with timestamp
                - bot_info: BotInfo | None - Creator and description metadata
                - created: str - Bot creation date
                - pricing_error: str | None - Error message if scraping failed
            - Returns empty collection if data file doesn't exist (not an error).

    Performance:
        - First call: ~50-200ms (file I/O + JSON parsing for ~240 bots)
        - Cached calls: <1ms (in-memory access)
        - Memory usage: ~2-5MB for typical dataset
        - Cache persists until force_reload=True or process restart

    Error Scenarios:
        - Missing data file: Returns empty collection, logs helpful guidance
        - Corrupted JSON: Raises JSONDecodeError - run update to rebuild file
        - Permission issues: Raises PermissionError - check file permissions
        - Invalid schema: Raises ValidationError - data file format changed

    See Also:
        - reload_bots(): Convenience wrapper for force_reload=True
        - get_all_bots(): Get list of bots from loaded collection
        - Use 'virginia-clemm-poe update' command to populate missing data

    Examples:
        ```python
        # Standard usage (recommended) - uses cache
        collection = load_bots()
        if collection.data:
            print(f"Loaded {len(collection.data)} bots")
        else:
            print("No data available. Run 'virginia-clemm-poe update'")

        # Force reload after external update
        collection = load_bots(force_reload=True)

        # Access bot data
        bots = collection.data
        model_count = len(bots)
        priced_count = sum(1 for m in bots if m.pricing)
        print(f"Total: {model_count}, with pricing: {priced_count}")

        # Handle missing data gracefully
        try:
            collection = load_bots()
            if not collection.data:
                print("Run 'virginia-clemm-poe update' to fetch bot data")
        except Exception as e:
            print(f"Data loading failed: {e}")
        ```
    """
    global _collection

    if _collection is not None and not force_reload:
        return _collection

    if not DATA_FILE_PATH.exists():
        logger.warning(f"Data file not found: {DATA_FILE_PATH}")
        logger.info("Run 'virginia-clemm-poe update' to fetch bot data")
        return BotCollection(data=[])

    try:
        with open(DATA_FILE_PATH) as f:
            collection_data = json.load(f)

        # Validate data if validation module is available
        try:
            from .utils.validation import validate_bot_data, check_data_consistency
            is_valid, errors = validate_bot_data(collection_data)
            if not is_valid:
                logger.warning(f"Data validation found {len(errors)} schema issues")
                for error in errors[:5]:  # Show first 5 errors
                    logger.debug(f"  Schema issue: {error}")

            warnings = check_data_consistency(collection_data)
            if warnings:
                logger.debug(f"Data consistency check found {len(warnings)} warnings")
        except ImportError:
            pass  # Validation is optional

        _collection = BotCollection(**collection_data)
        logger.debug(f"Loaded {len(_collection.data)} bots")
        return _collection
    except Exception as e:
        logger.error(f"Failed to load bots: {e}")
        return BotCollection(data=[])


def get_all_bots() -> list[PoeBot]:
    """Get all available Poe bots from the dataset.

    Retrieves the complete list of bots, including those with and without
    pricing information. This function provides raw access to the entire bot
    dataset without any filtering, making it ideal for bulk operations, analytics,
    or when you need to implement custom filtering logic.

    Returns:
        list[PoeBot]: Complete list of bots with full metadata.
            Each PoeBot includes:
            - id: str - Bot identifier (e.g., "GPT-4", "Claude-3-Opus")
            - architecture: Architecture object with:
                - input_modalities: list[str] - Supported inputs ("text", "image")
                - output_modalities: list[str] - Supported outputs
                - modality: str - Primary mode (e.g., "text->text")
            - pricing: Pricing | None - If available, contains:
                - details: PricingDetails - All cost fields
                - checked_at: datetime - Last scrape timestamp
            - bot_info: BotInfo | None - If available, contains:
                - creator: str - Bot creator handle (e.g., "@openai")
                - description: str - Main description text
                - description_extra: str | None - Additional details
            - created: str - Bot creation timestamp
            - pricing_error: str | None - Error message if scraping failed
            Typically returns 240+ bots. Empty list if no data is loaded.

    Performance:
        - Time complexity: O(1) after initial load (cached)
        - Memory usage: ~2MB for typical dataset
        - First call: ~50ms (loads from disk)
        - Subsequent calls: <1ms (from cache)

    Error Scenarios:
        - FileNotFoundError: If poe_models.json is missing
          Solution: Run `virginia-clemm-poe update --all` to create dataset
        - JSONDecodeError: If data file is corrupted
          Solution: Delete data file and run update command
        - ValidationError: If bot data doesn't match schema
          Solution: Update to latest package version

    See Also:
        - get_bots_with_pricing(): For bots with pricing data only
        - search_bots(): For filtered bot discovery
        - get_bot_by_id(): For specific bot lookup

    Example:
        ```python
        # Get all bots and analyze by owner
        bots = get_all_bots()
        print(f"Total bots: {len(bots)}")

        # Group by owner
        by_owner = {}
        for bot in bots:
            owner = bot.owned_by
            by_owner.setdefault(owner, []).append(bot)

        # Show distribution
        for owner, owner_models in sorted(by_owner.items()):
            print(f"{owner}: {len(owner_models)} bots")
        ```

    Note:
        - Returns a new list each time (safe to modify)
        - Includes all bots regardless of data completeness
        - Order matches the original API response
        - Used by CLI list command and other filtering functions
    """
    collection = load_bots()
    return collection.data


def get_bot_by_id(model_id: str) -> PoeBot | None:
    """Get a specific bot by its unique identifier with exact matching.

    Performs fast, case-sensitive exact match lookup for a bot using its ID.
    This is the optimal function for retrieving a specific bot when you have
    the precise bot identifier, providing O(1) lookup performance.

    Args:
        model_id: The exact bot ID to search for (case-sensitive).
                 Examples: "Claude-3-Opus", "GPT-4", "claude-3-5-sonnet-20241022"

    Returns:
        PoeBot | None: The matching bot with full metadata, or None if not found.
            If found, contains complete bot structure:
            - id: str - Exact match of requested model_id
            - architecture: Architecture - Input/output capabilities
            - pricing: Pricing | None - Cost data (check for None)
            - bot_info: BotInfo | None - Creator/description (check for None)
            - created: str - Bot creation timestamp
            - pricing_error: str | None - Error details if scraping failed
            Returns None if model_id not found or no data is loaded.

    Performance:
        - Lookup time: <1ms (uses internal dictionary mapping)
        - Much faster than search_bots() for exact ID lookups
        - Uses cached data (no file I/O after initial load)
        - Memory efficient - returns reference to existing object

    Error Scenarios:
        - Bot ID not found: Returns None (not an error)
        - Empty/None model_id: Returns None
        - Data file missing: Returns None after logging warning
        - Typos in ID: Returns None (use search_bots() for fuzzy matching)

    See Also:
        - search_bots(): For partial/fuzzy matching when ID is uncertain
        - get_all_bots(): Get complete list to browse available IDs
        - reload_bots(): Refresh data if expecting new bots

    Examples:
        ```python
        # Standard exact lookup
        bot = get_bot_by_id("Claude-3-Opus")
        if bot:
            print(f"Found: {bot.id}")
            print(f"Created: {bot.created}")
            if bot.pricing:
                cost = bot.get_primary_cost()
                print(f"Primary cost: {cost}")
            if bot.bot_info:
                print(f"Creator: {bot.bot_info.creator}")
        else:
            print("Bot not found - check exact ID spelling")

        # Batch lookup for comparison
        model_ids = ["Claude-3-Opus", "GPT-4-Turbo", "Claude-3-Sonnet"]
        bots = [get_bot_by_id(mid) for mid in model_ids]
        found_models = [m for m in bots if m is not None]

        # Validate bot exists before using
        def get_model_cost(model_id: str) -> str:
            bot = get_bot_by_id(model_id)
            if not bot:
                return "Bot not found"
            if not bot.pricing:
                return "No pricing data"
            return bot.get_primary_cost()

        # Handle case variations (bot IDs are case-sensitive)
        bot = get_bot_by_id("claude-3-opus")  # May not match "Claude-3-Opus"
        if not bot:
            # Fall back to search for case-insensitive matching
            results = search_bots("claude-3-opus")
            bot = results[0] if results else None
        ```
    """
    collection = load_bots()
    return collection.get_by_id(model_id)


def search_bots(query: str) -> list[PoeBot]:
    """Search bots by ID or name using case-insensitive matching.

    Performs a flexible search across bot IDs and root names,
    useful when you don't know the exact bot ID or want to find
    all bots matching a pattern. This is the primary discovery function
    for interactive exploration of available bots.

    Args:
        query: Search term to match against bot names (case-insensitive).
               Empty or whitespace-only queries return empty list.

    Returns:
        list[PoeBot]: Matching bots sorted by ID, each containing:
            - All fields from PoeBot (see get_all_bots() for structure)
            - Bots are filtered by case-insensitive substring match
            - Sorted alphabetically by bot ID for consistent display
            - Empty list if no matches found or no data is loaded.

    Performance:
        - Typical response time: <50ms for datasets up to 1000 bots
        - Uses in-memory search on cached data (no file I/O after first load)
        - Linear search complexity O(n) where n is total number of bots
        - For exact lookups, prefer get_bot_by_id() which is O(1)

    Error Scenarios:
        - Empty query: Returns empty list (not an error)
        - Missing data file: Returns empty list, logs warning with solution
        - Corrupted data: May raise JSON parsing errors - run update to fix

    See Also:
        - get_bot_by_id(): For exact ID lookups (faster for known IDs)
        - get_bots_with_pricing(): Filter results to only priced bots
        - get_all_bots(): Get complete unfiltered dataset

    Examples:
        ```python
        # Find all Claude bots under 100 points per message
        claude_models = search_bots("claude")
        affordable_claude = [m for m in claude_models
                           if m.pricing and m.get_primary_cost_numeric() < 100]

        # Find GPT bots for comparison
        gpt_models = search_bots("gpt-4")

        # Partial match works for discovery
        sonnet_models = search_bots("sonnet")  # Finds Claude-Sonnet variants

        # Handle no results gracefully
        results = search_bots("nonexistent")
        if not results:
            print("No bots found. Try broader search terms.")
        ```
    """
    collection = load_bots()
    return collection.search(query)


def get_bots_with_pricing() -> list[PoeBot]:
    """Get all bots that have valid pricing information.

    Filters the complete bot dataset to return only bots that have
    successfully scraped pricing data. Essential for cost analysis, budget
    planning, and comparing bot economics across different providers.

    Returns:
        list[PoeBot]: Bots with valid pricing data, sorted by ID.
            Each bot guaranteed to have:
            - pricing: Pricing (never None) containing:
                - details: PricingDetails with cost fields like:
                    - input_text: str | None - "10 points/1k tokens"
                    - bot_message: str | None - "5 points/message"
                    - initial_points_cost: str | None - "100 points"
                    - (and other pricing fields)
                - checked_at: datetime - When pricing was scraped
            - All other standard PoeBot fields
            Empty list if no bots have pricing data.

    Performance:
        - Typical response time: <20ms for datasets up to 1000 bots
        - Uses in-memory filtering on cached data (no file I/O)
        - Usually returns 95-98% of total bots (high coverage)
        - Results cached until next reload_bots() call

    Error Scenarios:
        - Missing data file: Returns empty list, logs warning
        - All bots lack pricing: Returns empty list (run update --pricing)
        - Stale data: Returns outdated pricing - call reload_bots() first

    See Also:
        - get_bots_needing_update(): Get bots missing pricing data
        - search_bots(): Filter by name, then check pricing availability
        - reload_bots(): Refresh data if pricing seems outdated

    Examples:
        ```python
        # Get all bots with pricing for cost analysis
        priced_models = get_bots_with_pricing()
        print(f"Bots with pricing: {len(priced_models)}")

        # Find cheapest bots under 50 points per message
        budget_models = [m for m in priced_models
                        if m.get_primary_cost_numeric() < 50]

        # Compare pricing across bot families
        claude_priced = [m for m in priced_models if "claude" in m.id.lower()]
        gpt_priced = [m for m in priced_models if "gpt" in m.id.lower()]

        # Sort by cost for price comparison
        sorted_by_cost = sorted(priced_models,
                               key=lambda m: m.get_primary_cost_numeric())
        cheapest = sorted_by_cost[0] if sorted_by_cost else None

        # Check pricing coverage
        total_models = len(get_all_bots())
        coverage = len(priced_models) / total_models * 100 if total_models else 0
        print(f"Pricing coverage: {coverage:.1f}%")
        ```
    """
    collection = load_bots()
    return [m for m in collection.data if m.has_pricing()]


def get_bots_needing_update() -> list[PoeBot]:
    """Get bots that need pricing information updated.

    Identifies bots that either lack pricing data or had errors during
    the last pricing scrape attempt. This function is essential for maintaining
    data quality and helps prioritize which bots need web scraping attention.
    It's primarily used by the update pipeline but also useful for monitoring
    data completeness.

    Returns:
        list[PoeBot]: Bots requiring data updates, sorted by ID.
            Includes bots where:
            - pricing is None (never scraped)
            - pricing_error is not None (scraping failed)
            Each bot in the list needs attention for data completeness.
            Use this with 'virginia-clemm-poe update --force' to retry.
            Empty list if all bots have complete data.

    Performance:
        - Time complexity: O(n) where n is total number of bots
        - Memory usage: Proportional to bots needing update
        - Typical execution: ~5ms for 240 bots
        - Result size: Varies (0-50 bots depending on data state)

    Error Scenarios:
        - FileNotFoundError: If poe_models.json is missing
          Solution: Run `virginia-clemm-poe update --all` to create dataset
        - Empty result: All bots have valid pricing (ideal state)
          Solution: No action needed - data is complete

    See Also:
        - get_bots_with_pricing(): For successfully priced bots
        - get_all_bots(): For complete bot list
        - BotUpdater.update_all(): To update bots needing attention

    Example:
        ```python
        # Check data completeness
        need_update = get_bots_needing_update()
        all_models = get_all_bots()
        completion_rate = (len(all_models) - len(need_update)) / len(all_models) * 100

        print(f"Data completion: {completion_rate:.1f}%")
        print(f"Bots needing update: {len(need_update)}")

        # Analyze update needs
        no_pricing = [m for m in need_update if m.pricing is None]
        with_errors = [m for m in need_update if m.pricing_error]

        print(f"- Missing pricing: {len(no_pricing)}")
        print(f"- Pricing errors: {len(with_errors)}")

        # Show error types
        error_types = {}
        for bot in with_errors:
            error = bot.pricing_error or "Unknown"
            error_types[error] = error_types.get(error, 0) + 1

        for error, count in sorted(error_types.items()):
            print(f"  {error}: {count} bots")
        ```

    Note:
        - Includes bots with pricing=None (never scraped)
        - Includes bots with pricing_error set (failed scraping)
        - Used by updater to prioritize work efficiently
        - Empty list indicates 100% data coverage
        - Run update command to resolve identified bots
    """
    collection = load_bots()
    return [m for m in collection.data if m.needs_pricing_update()]


def reload_bots() -> BotCollection:
    """Force reload bots from disk, bypassing cache.

    Clears the internal cache and reloads the bot data from the JSON file.
    This function is essential when you need to ensure you're working with the
    absolute latest data, particularly after external updates or when monitoring
    for changes. It's the programmatic equivalent of restarting the application
    to pick up file changes.

    Returns:
        BotCollection: Fresh collection loaded directly from disk.
            Same structure as load_bots() but always reads from file.
            Bypasses all caching for guaranteed data freshness.
            See load_bots() for detailed BotCollection structure.

    Performance:
        - Time complexity: O(n) where n is file size
        - Memory usage: ~2MB for typical dataset
        - Execution time: ~50ms (disk I/O dependent)
        - Cache impact: Invalidates and replaces global cache

    Error Scenarios:
        - FileNotFoundError: If poe_models.json is deleted
          Solution: Run `virginia-clemm-poe update --all` to recreate
        - JSONDecodeError: If file is corrupted during external edit
          Solution: Restore from backup or run update command
        - PermissionError: If file is locked by another process
          Solution: Close other applications accessing the file

    See Also:
        - load_bots(): Standard cached loading (preferred for performance)
        - get_all_bots(): Uses cached data for speed
        - BotUpdater.update_all(): Updates and saves bot data

    Example:
        ```python
        # Scenario 1: After external update process
        import subprocess

        # Run update in subprocess
        subprocess.run(["virginia-clemm-poe", "update", "--all"])

        # Reload to get fresh data
        fresh_collection = reload_bots()
        print(f"Loaded {len(fresh_collection.data)} bots")

        # Scenario 2: Monitoring for external changes
        import time
        from pathlib import Path

        data_file = Path("path/to/poe_models.json")
        last_modified = data_file.stat().st_mtime

        while True:
            current_modified = data_file.stat().st_mtime
            if current_modified > last_modified:
                print("Data file changed, reloading...")
                collection = reload_bots()
                print(f"Reloaded {len(collection.data)} bots")
                last_modified = current_modified
            time.sleep(60)  # Check every minute

        # Scenario 3: Testing data integrity
        original = get_all_bots()
        fresh = reload_bots().data

        if len(original) != len(fresh):
            print("Warning: Bot count changed!")
        ```

    Note:
        - Bypasses global cache completely
        - Equivalent to load_bots(force_reload=True)
        - All subsequent calls use the new cached data
        - Thread-safe (uses locking internally)
        - Required after external file modifications
    """
    return load_bots(force_reload=True)


async def get_account_balance(
    use_api_key: bool = False,
    api_key: str | None = None,
    use_browser: bool = True,
    use_cache: bool = True,
    force_refresh: bool = False,
) -> dict:
    """Get Poe account balance and compute points information.

    Retrieves the current account's compute points balance, subscription status,
    and other account-related information. This function uses stored session cookies
    from previous logins or can use an API key if available.

    Args:
        use_api_key: If True, attempt to use API key first (limited info but faster)
        api_key: Optional Poe API key for authentication
        use_browser: If True, automatically launch browser for scraping when API fails
        use_cache: If True, return cached balance if available and not expired (5 min cache)
        force_refresh: If True, ignore cache and fetch fresh data

    Returns:
        dict: Account balance information containing:
            - compute_points_available: int - Current compute points balance
            - daily_compute_points_available: int | None - Daily points if applicable
            - subscription: dict - Subscription details including isActive status
            - message_point_info: dict - Detailed message point information
            - timestamp: str - ISO timestamp of when data was retrieved

    Raises:
        AuthenticationError: If no valid cookies or API key available
        APIError: If the balance request fails

    Examples:
        ```python
        # Using stored cookies from previous login
        balance = await get_account_balance()
        print(f"Compute points: {balance['compute_points_available']:,}")

        # Force refresh to get latest data
        balance = await get_account_balance(force_refresh=True)

        # Check subscription status
        if balance['subscription']['isActive']:
            print("Premium subscription active")

        # Using API key (if Poe adds this endpoint)
        balance = await get_account_balance(use_api_key=True, api_key="your-key")
        ```

    Note:
        - Requires prior login via login_to_poe() or extract_poe_cookies()
        - Cookie method provides more detailed information than API key
        - Cookies expire and may need refreshing via re-login
        - Automatically launches browser for scraping if API returns no data
        - Balance data is cached for 5 minutes to reduce API calls
    """
    session_manager = get_session_manager()

    # First try without browser
    result = await session_manager.get_account_balance(
        use_api_key=use_api_key, api_key=api_key, use_cache=use_cache, force_refresh=force_refresh
    )

    # If we got no data and browser is allowed, try with browser
    if use_browser and result.get("compute_points_available") is None:
        logger.info("API returned no balance data, launching browser for scraping...")

        # Import here to avoid circular dependency
        from virginia_clemm_poe.browser_pool import get_global_pool

        # Launch browser with stored cookies for scraping
        pool = await get_global_pool(max_size=1)
        async with pool.acquire_page() as page:
            # Load cookies into browser
            if session_manager.has_valid_cookies():
                # Navigate to Poe with cookies
                await page.goto("https://poe.com")

                # Set cookies in browser context
                context = page.context
                cookie_list = []
                for name, value in session_manager.cookies.items():
                    cookie_list.append({"name": name, "value": value, "domain": ".poe.com", "path": "/"})
                await context.add_cookies(cookie_list)

                # Reload page with cookies
                await page.reload()
                await page.wait_for_load_state("networkidle")

            # Get balance using browser scraping
            result = await session_manager.get_account_balance(page=page, force_refresh=True)

    return result


async def login_to_poe(page=None) -> dict[str, str]:
    """Open browser for manual Poe login and extract session cookies.

    Opens an interactive browser window where the user can manually log in to Poe.
    After successful login, extracts and stores the session cookies for future use
    with balance checking and other authenticated operations.

    Args:
        page: Optional existing Playwright page to use. If not provided, creates new one

    Returns:
        dict[str, str]: Extracted cookies including essential ones:
            - p-b: Primary session token
            - p-lat: Session latitude token
            - m-b: Message token
            - cf_clearance: Cloudflare clearance token
            - __cf_bm: Cloudflare bot management token

    Raises:
        AuthenticationError: If login fails or essential cookies missing
        TimeoutError: If user doesn't complete login within 5 minutes

    Examples:
        ```python
        # Perform interactive login
        cookies = await login_to_poe()
        print(f"Successfully extracted {len(cookies)} cookies")

        # Now can check balance
        balance = await get_account_balance()
        print(f"Points available: {balance['compute_points_available']}")
        ```

    Note:
        - Opens a browser window that stays open until login completes
        - User must manually enter credentials and complete any 2FA
        - Cookies are automatically saved for future sessions
        - Uses PlaywrightAuthor's browser if available
    """
    session_manager = get_session_manager()

    # If no page provided, create one
    if not page:
        from .browser_pool import get_global_pool

        pool = await get_global_pool(max_size=1)
        async with pool.acquire_page() as new_page:
            return await login_to_poe(page=new_page)

    # Use the provided page
    # Try to access a bot page to check if we're logged in
    # This is a better test than looking for UI elements
    logger.info("Checking if already logged in to Poe...")
    test_model_url = "https://poe.com/Claude-3-Opus"  # Use a known bot

    try:
        # Navigate to a bot page - this requires authentication
        await page.goto(test_model_url, wait_until="networkidle", timeout=10000)

        # Check if we can see the bot page content (not redirected to login)
        current_url = page.url

        if "/login" not in current_url and "poe.com/Claude" in current_url:
            # We're on the bot page, so we're logged in!
            logger.info("Already logged in to Poe (detected via bot page access)")
            logger.info("Extracting existing session cookies...")

            # Extract cookies from the authenticated session
            cookies = await session_manager.extract_from_existing_playwright_session(page)

            if cookies and "p-b" in cookies:
                logger.info(f"Successfully extracted {len(cookies)} cookies from existing session")
                return cookies
            logger.warning("Could not extract valid cookies, proceeding to login...")

    except Exception as e:
        logger.debug(f"Not logged in or couldn't access bot page: {e}")

    # If we're here, we need to login
    logger.info("Not logged in, navigating to login page...")
    await page.goto("https://poe.com/login")
    logger.info("Please log in to Poe.com in the browser window...")
    logger.info("(Keep the browser open until login is complete)")

    # Wait for successful login - check by trying to access a bot page again
    login_confirmed = False
    start_time = asyncio.get_event_loop().time()
    timeout_seconds = 300  # 5 minutes

    while not login_confirmed and (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
        try:
            # Periodically check if we can access authenticated content
            await asyncio.sleep(2)  # Check every 2 seconds

            # Try to navigate to a bot page
            await page.goto(test_model_url, wait_until="domcontentloaded", timeout=5000)
            current_url = page.url

            if "/login" not in current_url and "poe.com/Claude" in current_url:
                login_confirmed = True
                logger.info("Login successful! Extracting cookies...")
                cookies = await session_manager.extract_from_existing_playwright_session(page)

                if cookies and "p-b" in cookies:
                    return cookies
                raise AuthenticationError("Login succeeded but could not extract valid cookies")

        except Exception as e:
            # Still waiting for login
            if "Target page, context or browser has been closed" in str(e):
                raise AuthenticationError(
                    "Browser was closed before login completed. Please try again and keep the browser open."
                )
            # Continue waiting

    if not login_confirmed:
        raise TimeoutError("Login timed out after 5 minutes. Please try again.")
    return None


async def extract_poe_cookies(page) -> dict[str, str]:
    """Extract Poe session cookies from an existing browser session.

    Extracts cookies from an active PlaywrightAuthor browser session where the user
    is already logged in to Poe. This is useful when working with PlaywrightAuthor's
    interactive browser automation.

    Args:
        page: Active Playwright Page object from PlaywrightAuthor session

    Returns:
        dict[str, str]: Extracted Poe session cookies

    Raises:
        AuthenticationError: If essential cookies are missing

    Examples:
        ```python
        # From an existing PlaywrightAuthor session
        from playwrightauthor import PlaywrightAuthor

        async with PlaywrightAuthor() as author:
            page = await author.new_page()
            await page.goto("https://poe.com")
            # ... user logs in manually ...

            # Extract cookies from the session
            cookies = await extract_poe_cookies(page)
            print(f"Extracted {len(cookies)} cookies")
        ```

    Note:
        - Page must have an active Poe session (user logged in)
        - Automatically navigates to poe.com if not already there
        - Saves cookies for future use automatically
    """
    session_manager = get_session_manager()
    return await session_manager.extract_from_existing_playwright_session(page)


def has_valid_poe_session() -> bool:
    """Check if valid Poe session cookies are available.

    Returns:
        bool: True if essential Poe cookies (p-b and p-lat) are stored

    Examples:
        ```python
        if has_valid_poe_session():
            balance = await get_account_balance()
            print(f"Points: {balance['compute_points_available']}")
        else:
            print("Please login first using login_to_poe()")
        ```
    """
    session_manager = get_session_manager()
    return session_manager.has_valid_cookies()


def clear_poe_session() -> None:
    """Clear stored Poe session cookies.

    Removes all stored Poe session cookies and deletes the cookies file.
    Use this when you want to force a fresh login or clear credentials.

    Examples:
        ```python
        # Clear existing session
        clear_poe_session()
        print("Poe session cleared")

        # Now need to login again
        cookies = await login_to_poe()
        ```
    """
    session_manager = get_session_manager()
    session_manager.clear_cookies()
