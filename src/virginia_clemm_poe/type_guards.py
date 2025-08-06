# this_file: src/virginia_clemm_poe/type_guards.py
"""Runtime type guards for Virginia Clemm Poe.

This module provides runtime type validation functions to ensure data integrity
when processing external API responses and user inputs. These guards help catch
type mismatches early and provide clear error messages.
"""

from typing import Any, TypeGuard

from loguru import logger

from .exceptions import APIError, ModelDataError
from .types import ModelFilterCriteria, PoeApiModelData, PoeApiResponse


def is_poe_api_model_data(value: Any) -> TypeGuard[PoeApiModelData]:
    """Type guard to validate individual model data from Poe API.

    Args:
        value: The value to check

    Returns:
        True if the value matches PoeApiModelData structure

    Example:
        >>> data = {"id": "model-1", "object": "model", "created": 12345, ...}
        >>> if is_poe_api_model_data(data):
        ...     # Safe to use as PoeApiModelData
        ...     model_id = data["id"]
    """
    if not isinstance(value, dict):
        return False

    # Check required fields
    required_fields = {"id", "object", "created", "owned_by", "permission", "root", "architecture"}
    if not all(field in value for field in required_fields):
        return False

    # Validate field types
    return (
        isinstance(value.get("id"), str)
        and value.get("object") == "model"
        and isinstance(value.get("created"), int)
        and isinstance(value.get("owned_by"), str)
        and isinstance(value.get("permission"), list)
        and isinstance(value.get("root"), str)
        and isinstance(value.get("architecture"), dict)
        and (value.get("parent") is None or isinstance(value.get("parent"), str))
    )


def is_poe_api_response(value: Any) -> TypeGuard[PoeApiResponse]:
    """Type guard to validate the complete Poe API response.

    Args:
        value: The value to check

    Returns:
        True if the value matches PoeApiResponse structure

    Example:
        >>> response = {"object": "list", "data": [...]}
        >>> if is_poe_api_response(response):
        ...     models = response["data"]
    """
    if not isinstance(value, dict):
        return False

    # Check basic structure
    if value.get("object") != "list" or "data" not in value:
        return False

    # Check if data is a list
    data = value.get("data")
    if not isinstance(data, list):
        return False

    # Validate each model in the data (optional but recommended)
    # This ensures all models in the response are valid
    return all(is_poe_api_model_data(model) for model in data)


def is_model_filter_criteria(value: Any) -> TypeGuard[ModelFilterCriteria]:
    """Type guard to validate model filter criteria from user input.

    Args:
        value: The value to check

    Returns:
        True if the value matches ModelFilterCriteria structure

    Example:
        >>> criteria = {"owned_by": "openai", "has_pricing": True}
        >>> if is_model_filter_criteria(criteria):
        ...     filtered = filter_models(criteria)
    """
    if not isinstance(value, dict):
        return False

    # All fields are optional, but if present must have correct types
    for key, value_item in value.items():
        if (
            key == "id"
            and not isinstance(value_item, str)
            or key == "name"
            and not isinstance(value_item, str)
            or key == "owned_by"
            and not isinstance(value_item, str)
            or key == "has_pricing"
            and not isinstance(value_item, bool)
            or key == "has_bot_info"
            and not isinstance(value_item, bool)
            or key in ["min_points", "max_points"]
            and not isinstance(value_item, int | float)
            or key in ["created_after", "created_before"]
            and not isinstance(value_item, int)
            or key
            not in [
                "id",
                "name",
                "owned_by",
                "has_pricing",
                "has_bot_info",
                "min_points",
                "max_points",
                "created_after",
                "created_before",
            ]
        ):
            return False

    return True


def validate_poe_api_response(response: Any) -> PoeApiResponse:
    """Validate and return a Poe API response with proper error handling.

    Args:
        response: The response data to validate

    Returns:
        The validated PoeApiResponse

    Raises:
        APIError: If the response doesn't match expected structure

    Example:
        >>> raw_response = await fetch_from_api()
        >>> validated = validate_poe_api_response(raw_response)
        >>> # Now safe to use validated["data"]
    """
    if not is_poe_api_response(response):
        # Log detailed validation failure
        logger.error(f"Invalid API response structure: {type(response)}")

        # Provide helpful error message
        if not isinstance(response, dict):
            raise APIError("API response is not a dictionary. Expected format: {'object': 'list', 'data': [...]}")

        if response.get("object") != "list":
            raise APIError(f"API response has incorrect 'object' field: {response.get('object')}. Expected 'list'.")

        if "data" not in response:
            raise APIError("API response missing 'data' field. Expected format: {'object': 'list', 'data': [...]}")

        # If we get here, the data field has issues
        data = response.get("data", [])
        if not isinstance(data, list):
            raise APIError(f"API response 'data' field is not a list: {type(data)}. Expected list of model objects.")

        # Check for invalid models in data
        for i, model in enumerate(data[:5]):  # Check first 5 for performance
            if not is_poe_api_model_data(model):
                logger.error(f"Invalid model at index {i}: {model}")
                raise APIError(
                    f"API response contains invalid model data at index {i}. "
                    "Model must have fields: id, object, created, owned_by, permission, root, architecture."
                )

        raise APIError("API response validation failed for unknown reason")

    return response


def validate_model_filter_criteria(criteria: Any) -> ModelFilterCriteria:
    """Validate and return model filter criteria with proper error handling.

    Args:
        criteria: The filter criteria to validate

    Returns:
        The validated ModelFilterCriteria

    Raises:
        ModelDataError: If the criteria doesn't match expected structure

    Example:
        >>> user_input = {"owned_by": "openai", "invalid_field": 123}
        >>> validated = validate_model_filter_criteria(user_input)
        >>> # Raises ModelDataError about invalid_field
    """
    if not is_model_filter_criteria(criteria):
        if not isinstance(criteria, dict):
            raise ModelDataError(f"Filter criteria must be a dictionary, got {type(criteria).__name__}")

        # Check for invalid fields
        valid_fields = {
            "id",
            "name",
            "owned_by",
            "has_pricing",
            "has_bot_info",
            "min_points",
            "max_points",
            "created_after",
            "created_before",
        }
        invalid_fields = set(criteria.keys()) - valid_fields
        if invalid_fields:
            raise ModelDataError(
                f"Invalid filter fields: {', '.join(invalid_fields)}. "
                f"Valid fields are: {', '.join(sorted(valid_fields))}"
            )

        # Check for type mismatches
        type_errors = []
        for key, value in criteria.items():
            if (
                key == "has_pricing"
                and not isinstance(value, bool)
                or key == "has_bot_info"
                and not isinstance(value, bool)
            ):
                type_errors.append(f"{key} must be boolean, got {type(value).__name__}")
            elif key in ["min_points", "max_points"] and not isinstance(value, int | float):
                type_errors.append(f"{key} must be number, got {type(value).__name__}")
            elif key in ["created_after", "created_before"] and not isinstance(value, int):
                type_errors.append(f"{key} must be integer, got {type(value).__name__}")
            elif key in ["id", "name", "owned_by"] and not isinstance(value, str):
                type_errors.append(f"{key} must be string, got {type(value).__name__}")

        if type_errors:
            raise ModelDataError("Filter criteria type errors:\n" + "\n".join(f"  - {err}" for err in type_errors))

    return criteria  # type: ignore[no-any-return]
