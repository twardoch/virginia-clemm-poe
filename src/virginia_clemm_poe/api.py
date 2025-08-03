# this_file: src/virginia_clemm_poe/api.py

"""Public API for Virginia Clemm Poe."""

import json
from pathlib import Path
from typing import List, Optional

from loguru import logger

from .config import DATA_FILE_PATH
from .models import ModelCollection, PoeModel

_collection: Optional[ModelCollection] = None


def load_models(force_reload: bool = False) -> ModelCollection:
    """Load model collection from data file."""
    global _collection
    
    if _collection is not None and not force_reload:
        return _collection
    
    if not DATA_FILE_PATH.exists():
        logger.warning(f"Data file not found: {DATA_FILE_PATH}")
        logger.info("Run 'virginia-clemm-poe update' to fetch model data")
        return ModelCollection(data=[])
    
    try:
        with open(DATA_FILE_PATH, "r") as f:
            data = json.load(f)
        _collection = ModelCollection(**data)
        logger.debug(f"Loaded {len(_collection.data)} models")
        return _collection
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return ModelCollection(data=[])


def get_all_models() -> List[PoeModel]:
    """Get all available models."""
    collection = load_models()
    return collection.data


def get_model_by_id(model_id: str) -> Optional[PoeModel]:
    """Get a specific model by ID."""
    collection = load_models()
    return collection.get_by_id(model_id)


def search_models(query: str) -> List[PoeModel]:
    """Search models by ID or name."""
    collection = load_models()
    return collection.search(query)


def get_models_with_pricing() -> List[PoeModel]:
    """Get all models that have pricing information."""
    collection = load_models()
    return [m for m in collection.data if m.has_pricing()]


def get_models_needing_update() -> List[PoeModel]:
    """Get models that need pricing update."""
    collection = load_models()
    return [m for m in collection.data if m.needs_pricing_update()]


def reload_models() -> ModelCollection:
    """Force reload models from disk."""
    return load_models(force_reload=True)