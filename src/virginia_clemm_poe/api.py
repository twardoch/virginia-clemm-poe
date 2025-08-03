# this_file: src/virginia_clemm_poe/api.py

"""Public API for Virginia Clemm Poe."""

import json

from loguru import logger

from .config import DATA_FILE_PATH
from .models import ModelCollection, PoeModel

_collection: ModelCollection | None = None


def load_models(force_reload: bool = False) -> ModelCollection:
    """Load model collection from the data file with caching.
    
    This function loads the complete Poe model dataset from the JSON file,
    with automatic caching to avoid repeated file I/O operations.
    
    Args:
        force_reload: If True, bypasses cache and reloads from file
    
    Returns:
        ModelCollection containing all available models
    
    Note:
        - Uses global caching for performance
        - Returns empty collection if data file doesn't exist
        - Logs helpful messages for troubleshooting
        - Used internally by all other API functions
    
    Example:
        ```python
        # Load with cache (recommended)
        collection = load_models()
        
        # Force reload from disk
        collection = load_models(force_reload=True)
        ```
    """
    global _collection

    if _collection is not None and not force_reload:
        return _collection

    if not DATA_FILE_PATH.exists():
        logger.warning(f"Data file not found: {DATA_FILE_PATH}")
        logger.info("Run 'virginia-clemm-poe update' to fetch model data")
        return ModelCollection(data=[])

    try:
        with open(DATA_FILE_PATH) as f:
            data = json.load(f)
        _collection = ModelCollection(**data)
        logger.debug(f"Loaded {len(_collection.data)} models")
        return _collection
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return ModelCollection(data=[])


def get_all_models() -> list[PoeModel]:
    """Get all available Poe models from the dataset.
    
    Retrieves the complete list of models, including those with and without
    pricing information. This is the primary function for accessing the
    full model dataset.
    
    Returns:
        List of all PoeModel instances in the dataset
    
    Note:
        - Uses cached data from load_models() for performance
        - Returns empty list if no data file exists
        - Used by CLI list command and other filtering functions
    
    Example:
        ```python
        models = get_all_models()
        print(f"Total models: {len(models)}")
        
        for model in models:
            print(f"{model.id}: {model.architecture.modality}")
        ```
    """
    collection = load_models()
    return collection.data


def get_model_by_id(model_id: str) -> PoeModel | None:
    """Get a specific model by its unique identifier.
    
    Performs exact match lookup for a model using its ID. This is the
    most efficient way to retrieve a specific model when you know its ID.
    
    Args:
        model_id: The exact model ID to search for (case-sensitive)
    
    Returns:
        The matching PoeModel instance, or None if not found
    
    Note:
        - Uses case-sensitive exact matching
        - More efficient than search_models() for exact lookups
        - Used by CLI for displaying specific model details
    
    Example:
        ```python
        model = get_model_by_id("Claude-3-Opus")
        if model:
            print(f"Found: {model.id}")
            if model.pricing:
                print(f"Cost: {model.get_primary_cost()}")
        else:
            print("Model not found")
        ```
    """
    collection = load_models()
    return collection.get_by_id(model_id)


def search_models(query: str) -> list[PoeModel]:
    """Search models by ID or name using case-insensitive matching.
    
    Performs a flexible search across model IDs and root names,
    useful when you don't know the exact model ID or want to find
    all models matching a pattern.
    
    Args:
        query: Search term to match against model names (case-insensitive)
    
    Returns:
        List of matching PoeModel instances (may be empty)
    
    Note:
        - Searches both 'id' and 'root' fields
        - Uses case-insensitive substring matching
        - Used by CLI search command for user-friendly model discovery
    
    Example:
        ```python
        # Find all Claude models
        claude_models = search_models("claude")
        
        # Find GPT models
        gpt_models = search_models("gpt")
        
        # Partial match works too
        models = search_models("son")  # Finds "Claude-Sonnet-3.5" etc.
        ```
    """
    collection = load_models()
    return collection.search(query)


def get_models_with_pricing() -> list[PoeModel]:
    """Get all models that have valid pricing information.
    
    Filters the complete model dataset to return only models that have
    successfully scraped pricing data. Useful for displaying cost information
    or analyzing pricing patterns.
    
    Returns:
        List of PoeModel instances that have pricing data
    
    Note:
        - Excludes models with pricing errors or missing pricing
        - Used by CLI list --with-pricing command
        - Each returned model will have model.pricing != None
    
    Example:
        ```python
        priced_models = get_models_with_pricing()
        print(f"Models with pricing: {len(priced_models)}")
        
        for model in priced_models:
            cost = model.get_primary_cost()
            print(f"{model.id}: {cost}")
        ```
    """
    collection = load_models()
    return [m for m in collection.data if m.has_pricing()]


def get_models_needing_update() -> list[PoeModel]:
    """Get models that need pricing information updated.
    
    Identifies models that either lack pricing data or had errors during
    the last pricing scrape attempt. This is used by the updater to determine
    which models require attention.
    
    Returns:
        List of PoeModel instances needing pricing updates
    
    Note:
        - Includes models with no pricing data (pricing=None)
        - Includes models with pricing errors (pricing_error != None)
        - Used by updater.py to prioritize scraping work
        - Excludes models with valid, recent pricing data
    
    Example:
        ```python
        need_update = get_models_needing_update()
        print(f"Models needing update: {len(need_update)}")
        
        for model in need_update:
            if model.pricing_error:
                print(f"{model.id}: Error - {model.pricing_error}")
            else:
                print(f"{model.id}: No pricing data")
        ```
    """
    collection = load_models()
    return [m for m in collection.data if m.needs_pricing_update()]


def reload_models() -> ModelCollection:
    """Force reload models from disk, bypassing cache.
    
    Clears the internal cache and reloads the model data from the JSON file.
    Useful when the data file has been updated externally or when you want
    to ensure you have the latest data.
    
    Returns:
        Fresh ModelCollection loaded from disk
    
    Note:
        - Bypasses the global cache maintained by load_models()
        - Equivalent to load_models(force_reload=True)
        - Used when data freshness is critical
        - Updates the internal cache with new data
    
    Example:
        ```python
        # After running update command, reload to see new data
        fresh_collection = reload_models()
        models = fresh_collection.data
        print(f"Reloaded {len(models)} models")
        ```
    """
    return load_models(force_reload=True)
