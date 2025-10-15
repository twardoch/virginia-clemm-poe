# this_file: src/virginia_clemm_poe/utils/validation.py

"""JSON Schema validation for bot data integrity."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


def get_bot_schema() -> dict[str, Any]:
    """Get the JSON schema for bot data validation.

    Returns:
        JSON schema dictionary for validating bot data structure.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["object", "data"],
        "properties": {
            "object": {
                "type": "string",
                "const": "list"
            },
            "data": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "object", "created", "owned_by", "root"],
                    "properties": {
                        "id": {"type": "string", "minLength": 1},
                        "object": {"type": "string", "const": "model"},
                        "created": {"type": "integer", "minimum": 0},
                        "owned_by": {"type": "string", "minLength": 1},
                        "permission": {"type": "array"},
                        "root": {"type": "string", "minLength": 1},
                        "parent": {"type": ["string", "null"]},
                        "architecture": {
                            "type": "object",
                            "required": ["input_modalities", "output_modalities", "modality"],
                            "properties": {
                                "input_modalities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1
                                },
                                "output_modalities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1
                                },
                                "modality": {"type": "string", "minLength": 1}
                            }
                        },
                        "pricing": {
                            "type": ["object", "null"],
                            "properties": {
                                "api": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "prompt": {"type": ["string", "null"]},
                                        "completion": {"type": ["string", "null"]},
                                        "image": {"type": ["string", "null"]},
                                        "request": {"type": ["string", "null"]}
                                    }
                                },
                                "scraped": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "checked_at": {"type": "string"},
                                        "details": {"type": "object"}
                                    }
                                }
                            }
                        },
                        "api_last_updated": {"type": ["string", "null"]},
                        "pricing_error": {"type": ["string", "null"]},
                        "bot_info": {
                            "type": ["object", "null"],
                            "properties": {
                                "creator": {"type": ["string", "null"]},
                                "description": {"type": ["string", "null"]},
                                "description_extra": {"type": ["string", "null"]}
                            }
                        }
                    }
                }
            }
        }
    }


def validate_bot_data(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate bot data against the JSON schema.

    Args:
        data: Bot data dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        import jsonschema
    except ImportError:
        logger.warning("jsonschema not installed, skipping validation")
        return True, []

    schema = get_bot_schema()
    validator = jsonschema.Draft7Validator(schema)

    errors = []
    for error in validator.iter_errors(data):
        error_path = " -> ".join(str(p) for p in error.path)
        if error_path:
            errors.append(f"[{error_path}] {error.message}")
        else:
            errors.append(error.message)

    return len(errors) == 0, errors


def check_data_consistency(data: dict[str, Any]) -> list[str]:
    """Check for data consistency issues in bot data.

    Args:
        data: Bot data dictionary to check

    Returns:
        List of consistency warnings
    """
    warnings = []

    if "data" not in data:
        return ["Missing 'data' field"]

    for i, bot in enumerate(data["data"]):
        bot_id = bot.get("id", f"Bot {i}")

        # Check for pricing consistency
        if pricing := bot.get("pricing"):
            if api_pricing := pricing.get("api"):
                # Check if API pricing has at least one value
                has_api = any(api_pricing.get(f) for f in ["prompt", "completion", "image", "request"])
                if not has_api:
                    warnings.append(f"{bot_id}: API pricing present but all values null")

            if scraped := pricing.get("scraped"):
                # Check timestamp format
                if checked_at := scraped.get("checked_at"):
                    try:
                        datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        warnings.append(f"{bot_id}: Invalid timestamp format in scraped pricing: {checked_at}")

        # Check for required fields in bot_info
        if bot_info := bot.get("bot_info"):
            if not bot_info.get("creator") and not bot_info.get("description"):
                warnings.append(f"{bot_id}: Bot info present but missing creator and description")

        # Check architecture consistency
        if arch := bot.get("architecture"):
            input_mods = arch.get("input_modalities", [])
            output_mods = arch.get("output_modalities", [])
            modality = arch.get("modality", "")

            # Validate modality string matches input/output
            if "->" in modality:
                expected_parts = modality.split("->")
                if len(expected_parts) == 2:
                    input_type, output_type = expected_parts
                    # Basic validation - could be enhanced
                    if "text" in input_type and "text" not in input_mods:
                        warnings.append(f"{bot_id}: Modality '{modality}' doesn't match input_modalities {input_mods}")

    return warnings


def validate_model_id(model_id: str, valid_ids: list[str]) -> tuple[bool, str | None]:
    """Validate and suggest corrections for model IDs.

    Args:
        model_id: The model ID to validate
        valid_ids: List of valid model IDs

    Returns:
        Tuple of (is_valid, suggested_id)
    """
    # Exact match
    if model_id in valid_ids:
        return True, None

    # Case-insensitive match
    lower_id = model_id.lower()
    for valid_id in valid_ids:
        if valid_id.lower() == lower_id:
            return False, valid_id

    # Fuzzy matching (simple substring search)
    suggestions = []
    for valid_id in valid_ids:
        if lower_id in valid_id.lower() or valid_id.lower() in lower_id:
            suggestions.append(valid_id)

    if len(suggestions) == 1:
        return False, suggestions[0]
    elif len(suggestions) > 1:
        # Return the shortest match as the best suggestion
        return False, min(suggestions, key=len)

    return False, None


def validate_data_file(file_path: Path) -> tuple[bool, list[str], list[str]]:
    """Validate a bot data file comprehensively.

    Args:
        file_path: Path to the JSON data file

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    if not file_path.exists():
        return False, [f"File not found: {file_path}"], []

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], []
    except Exception as e:
        return False, [f"Error reading file: {e}"], []

    # Schema validation
    is_valid, schema_errors = validate_bot_data(data)

    # Consistency checks
    consistency_warnings = check_data_consistency(data)

    return is_valid, schema_errors, consistency_warnings