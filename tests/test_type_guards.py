# this_file: tests/test_type_guards.py
"""Tests for runtime type validation functions."""

from typing import Any

import pytest

from virginia_clemm_poe.exceptions import APIError, ModelDataError
from virginia_clemm_poe.type_guards import (
    is_model_filter_criteria,
    is_poe_api_model_data,
    is_poe_api_response,
    validate_model_filter_criteria,
    validate_poe_api_response,
)


class TestIsPoeApiModelData:
    """Test is_poe_api_model_data type guard."""

    def test_valid_model_data(self, sample_api_response_data: dict[str, Any]) -> None:
        """Test type guard with valid model data."""
        model_data = sample_api_response_data["data"][0]
        assert is_poe_api_model_data(model_data)

    def test_invalid_model_data_not_dict(self) -> None:
        """Test type guard with non-dictionary input."""
        assert not is_poe_api_model_data("not a dict")
        assert not is_poe_api_model_data([1, 2, 3])
        assert not is_poe_api_model_data(None)

    def test_invalid_model_data_missing_required_fields(self) -> None:
        """Test type guard with missing required fields."""
        incomplete_data = {
            "id": "test-model",
            "object": "model",
            # Missing: created, owned_by, permission, root, architecture
        }
        assert not is_poe_api_model_data(incomplete_data)

    def test_invalid_model_data_wrong_field_types(self) -> None:
        """Test type guard with incorrect field types."""
        wrong_types = {
            "id": 123,  # Should be string
            "object": "model",
            "created": "not-a-number",  # Should be int
            "owned_by": "testorg",
            "permission": "not-a-list",  # Should be list
            "root": "test-model",
            "architecture": "not-a-dict",  # Should be dict
        }
        assert not is_poe_api_model_data(wrong_types)

    def test_invalid_model_data_wrong_object_type(self) -> None:
        """Test type guard with incorrect object field value."""
        wrong_object = {
            "id": "test-model",
            "object": "not-model",  # Should be "model"
            "created": 1704369600,
            "owned_by": "testorg",
            "permission": [],
            "root": "test-model",
            "architecture": {},
        }
        assert not is_poe_api_model_data(wrong_object)

    def test_valid_model_data_with_optional_parent(self) -> None:
        """Test type guard with optional parent field."""
        with_parent = {
            "id": "test-model",
            "object": "model",
            "created": 1704369600,
            "owned_by": "testorg",
            "permission": [],
            "root": "test-model",
            "parent": "parent-model",  # Optional field
            "architecture": {},
        }
        assert is_poe_api_model_data(with_parent)

    def test_valid_model_data_with_null_parent(self) -> None:
        """Test type guard with null parent field."""
        with_null_parent = {
            "id": "test-model",
            "object": "model",
            "created": 1704369600,
            "owned_by": "testorg",
            "permission": [],
            "root": "test-model",
            "parent": None,  # Null is allowed
            "architecture": {},
        }
        assert is_poe_api_model_data(with_null_parent)


class TestIsPoeApiResponse:
    """Test is_poe_api_response type guard."""

    def test_valid_api_response(self, sample_api_response_data: dict[str, Any]) -> None:
        """Test type guard with valid API response."""
        assert is_poe_api_response(sample_api_response_data)

    def test_invalid_api_response_not_dict(self) -> None:
        """Test type guard with non-dictionary input."""
        assert not is_poe_api_response("not a dict")
        assert not is_poe_api_response([])
        assert not is_poe_api_response(None)

    def test_invalid_api_response_wrong_object_field(self) -> None:
        """Test type guard with incorrect object field."""
        wrong_object = {
            "object": "not-list",  # Should be "list"
            "data": [],
        }
        assert not is_poe_api_response(wrong_object)

    def test_invalid_api_response_missing_data_field(self) -> None:
        """Test type guard with missing data field."""
        missing_data = {
            "object": "list"
            # Missing: data
        }
        assert not is_poe_api_response(missing_data)

    def test_invalid_api_response_data_not_list(self) -> None:
        """Test type guard with non-list data field."""
        data_not_list = {"object": "list", "data": "not a list"}
        assert not is_poe_api_response(data_not_list)

    def test_valid_api_response_empty_data(self) -> None:
        """Test type guard with empty data array."""
        empty_data = {"object": "list", "data": []}
        assert is_poe_api_response(empty_data)

    def test_invalid_api_response_invalid_model_in_data(self) -> None:
        """Test type guard with invalid model in data array."""
        invalid_model = {
            "object": "list",
            "data": [
                {
                    "id": "incomplete-model"
                    # Missing required fields
                }
            ],
        }
        assert not is_poe_api_response(invalid_model)


class TestIsModelFilterCriteria:
    """Test is_model_filter_criteria type guard."""

    def test_valid_empty_criteria(self) -> None:
        """Test type guard with empty filter criteria."""
        assert is_model_filter_criteria({})

    def test_valid_criteria_with_string_fields(self) -> None:
        """Test type guard with valid string fields."""
        criteria = {"id": "test-model", "name": "Test Model", "owned_by": "testorg"}
        assert is_model_filter_criteria(criteria)

    def test_valid_criteria_with_boolean_fields(self) -> None:
        """Test type guard with valid boolean fields."""
        criteria = {"has_pricing": True, "has_bot_info": False}
        assert is_model_filter_criteria(criteria)

    def test_valid_criteria_with_numeric_fields(self) -> None:
        """Test type guard with valid numeric fields."""
        criteria = {"min_points": 10, "max_points": 100.5, "created_after": 1704369600, "created_before": 1704456000}
        assert is_model_filter_criteria(criteria)

    def test_invalid_criteria_not_dict(self) -> None:
        """Test type guard with non-dictionary input."""
        assert not is_model_filter_criteria("not a dict")
        assert not is_model_filter_criteria([])
        assert not is_model_filter_criteria(None)

    def test_invalid_criteria_wrong_field_types(self) -> None:
        """Test type guard with incorrect field types."""
        wrong_types = {
            "id": 123,  # Should be string
            "has_pricing": "yes",  # Should be boolean
            "min_points": "ten",  # Should be number
        }
        assert not is_model_filter_criteria(wrong_types)

    def test_invalid_criteria_unknown_fields(self) -> None:
        """Test type guard with unknown fields."""
        unknown_field = {"unknown_field": "value"}
        assert not is_model_filter_criteria(unknown_field)


class TestValidatePoeApiResponse:
    """Test validate_poe_api_response function."""

    def test_validate_valid_response(self, sample_api_response_data: dict[str, Any]) -> None:
        """Test validation with valid API response."""
        result = validate_poe_api_response(sample_api_response_data)
        assert result == sample_api_response_data

    def test_validate_invalid_response_not_dict(self) -> None:
        """Test validation with non-dictionary input."""
        with pytest.raises(APIError, match="API response is not a dictionary"):
            validate_poe_api_response("not a dict")

    def test_validate_invalid_response_wrong_object(self) -> None:
        """Test validation with incorrect object field."""
        wrong_object = {"object": "not-list", "data": []}
        with pytest.raises(APIError, match="incorrect 'object' field"):
            validate_poe_api_response(wrong_object)

    def test_validate_invalid_response_missing_data(self) -> None:
        """Test validation with missing data field."""
        missing_data = {"object": "list"}
        with pytest.raises(APIError, match="missing 'data' field"):
            validate_poe_api_response(missing_data)

    def test_validate_invalid_response_data_not_list(self) -> None:
        """Test validation with non-list data field."""
        data_not_list = {"object": "list", "data": "not a list"}
        with pytest.raises(APIError, match="'data' field is not a list"):
            validate_poe_api_response(data_not_list)

    def test_validate_invalid_model_in_data(self) -> None:
        """Test validation with invalid model in data array."""
        invalid_model = {
            "object": "list",
            "data": [
                {
                    "id": "incomplete-model"
                    # Missing required fields
                }
            ],
        }
        with pytest.raises(APIError, match="invalid model data at index 0"):
            validate_poe_api_response(invalid_model)


class TestValidateModelFilterCriteria:
    """Test validate_model_filter_criteria function."""

    def test_validate_valid_criteria(self) -> None:
        """Test validation with valid filter criteria."""
        criteria = {"owned_by": "testorg", "has_pricing": True}
        result = validate_model_filter_criteria(criteria)
        assert result == criteria

    def test_validate_invalid_criteria_not_dict(self) -> None:
        """Test validation with non-dictionary input."""
        with pytest.raises(ModelDataError, match="must be a dictionary"):
            validate_model_filter_criteria("not a dict")

    def test_validate_invalid_criteria_unknown_fields(self) -> None:
        """Test validation with unknown fields."""
        unknown_field = {"unknown_field": "value", "another_unknown": 123}
        with pytest.raises(ModelDataError, match="Invalid filter fields: another_unknown, unknown_field"):
            validate_model_filter_criteria(unknown_field)

    def test_validate_invalid_criteria_type_errors(self) -> None:
        """Test validation with type errors."""
        type_errors = {
            "has_pricing": "yes",  # Should be boolean
            "min_points": "ten",  # Should be number
            "id": 123,  # Should be string
        }
        with pytest.raises(ModelDataError, match="Filter criteria type errors"):
            validate_model_filter_criteria(type_errors)

    def test_validate_empty_criteria(self) -> None:
        """Test validation with empty criteria."""
        result = validate_model_filter_criteria({})
        assert result == {}
