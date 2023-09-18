"""Field Validator test cases."""
from unittest.mock import Mock

import pytest
from typing_extensions import Self

from src.esxport import EsXport
from src.exceptions import FieldNotFoundError


class TestValidateFields:
    """Test that all expected fields exist in all indices."""

    def test_all_expected_fields_exist_in_all_indices(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Test that all expected fields exist in all indices, me hearties!."""
        # Mock the get_mapping method of ElasticsearchClient to return a mapping with all expected fields
        mocker.patch.object(
            esxport_obj.es_client,
            "get_mapping",
            return_value={
                "index1": {
                    "mappings": {
                        "properties": ["field1", "field2", "field3"],
                    },
                },
                "index2": {
                    "mappings": {
                        "properties": ["field1", "field2", "field3"],
                    },
                },
            },
        )

        esxport_obj._validate_fields()

    def test_all_expected_fields_exist_in_some_indices(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Ahoy!.Test that all expected fields exist in some indices, me mateys!."""
        # Mock the get_mapping method of ElasticsearchClient to return a mapping with some expected fields
        mocker.patch.object(
            esxport_obj.es_client,
            "get_mapping",
            return_value={
                "index1": {
                    "mappings": {
                        "properties": ["aaa", "bbb"],
                    },
                },
                "index2": {
                    "mappings": {
                        "properties": ["cccc", "dddd"],
                    },
                },
            },
        )

        with pytest.raises(FieldNotFoundError):
            esxport_obj._validate_fields()

    def test_all_expected_fields_exist_in_one_index(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Test that all expected fields exist in one index, me hearties!."""
        # Mock the get_mapping method of ElasticsearchClient to return a mapping with all expected fields
        mocker.patch.object(
            esxport_obj.es_client,
            "get_mapping",
            return_value={
                "index1": {
                    "mappings": {
                        "properties": ["field1", "field2", "field3"],
                    },
                },
            },
        )

        esxport_obj.opts.index_prefixes = ["index1"]
        esxport_obj.opts.fields = ["field1", "field2", "field3"]
        esxport_obj._validate_fields()

    def test_sort_param_are_checked(self: Self, mocker: Mock, esxport_obj: EsXport) -> None:
        """Test that all expected fields exist in one index, me hearties!."""
        # Mock the get_mapping method of ElasticsearchClient to return a mapping with all expected fields
        mocker.patch.object(
            esxport_obj.es_client,
            "get_mapping",
            return_value={
                "index1": {
                    "mappings": {
                        "properties": ["field1", "field2", "field3"],
                    },
                },
            },
        )

        esxport_obj.opts.index_prefixes = ["index1"]
        esxport_obj.opts.sort = [{"abc": "desc"}, {"def": "desc"}]

        with pytest.raises(FieldNotFoundError):
            esxport_obj._validate_fields()

        esxport_obj.opts.sort = [{"field1": "asc"}, {"field2": "desc"}]

        esxport_obj._validate_fields()
