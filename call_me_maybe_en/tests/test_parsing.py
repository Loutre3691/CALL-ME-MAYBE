"""Unit tests for the parsing of prompts and functions."""

from typing import Any
from src.parsing import ConfigParsing
import pytest


def test_prompt_bad_key() -> None:
    configparsing = ConfigParsing()
    with pytest.raises(SystemExit):
        configparsing.parse_prompt_input(
            [{2: "greet john"}])  # type: ignore[dict-item]


def test_prompt_missing_value() -> None:
    configparsing = ConfigParsing()
    with pytest.raises(SystemExit):
        configparsing.parse_prompt_input([{"prompt": ""}])


def test_prompt_bad_value() -> None:
    configparsing = ConfigParsing()
    with pytest.raises(SystemExit):
        configparsing.parse_prompt_input([{"prompt": 3}])


def test_prompt_input_valid() -> None:
    contain = [{"prompt": "greet john"}]
    configparsing = ConfigParsing()

    result = configparsing.parse_prompt_input(contain)
    assert result[0].prompt == contain[0]["prompt"]
    assert len(result) == len(contain)


def test_list_empty() -> None:
    configparsing = ConfigParsing()

    with pytest.raises(SystemExit):
        configparsing.parse_prompt_input([])


def test_prompt_random() -> None:
    configparsing = ConfigParsing()

    with pytest.raises(SystemExit):
        configparsing.parse_prompt_input(42)  # type: ignore[arg-type]


def valid_function() -> dict[str, Any]:
    """Return a valid function definition, used as the base of the tests."""
    return {
        "name": "fn_greet",
        "description": "Greet someone.",
        "parameters": {"name": {"type": "string"}},
        "returns": {"type": "string"},
    }


def test_functions_valid() -> None:
    config = ConfigParsing()
    contain = [valid_function(), valid_function()]

    result = config.parse_prompt_functions(contain)

    assert len(result) == len(contain)
    assert result[0].name == "fn_greet"


def test_functions_not_list() -> None:
    config = ConfigParsing()
    with pytest.raises(SystemExit):
        config.parse_prompt_functions(42)  # type: ignore[arg-type]


def test_functions_empty_list() -> None:
    config = ConfigParsing()
    with pytest.raises(SystemExit):
        config.parse_prompt_functions([])


def test_functions_missing_name() -> None:
    data = valid_function()
    del data["name"]
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])


def test_functions_missing_description() -> None:
    data = valid_function()
    del data["description"]
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])


def test_functions_missing_parameters() -> None:
    data = valid_function()
    del data["parameters"]
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])


def test_functions_missing_returns() -> None:
    data = valid_function()
    del data["returns"]
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])


def test_functions_parameters_not_dict() -> None:
    data = valid_function()
    data["parameters"] = 5
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])


def test_parameters_bool() -> None:
    data = valid_function()
    data["parameters"]["name"]["type"] = "bool"
    with pytest.raises(SystemExit):
        ConfigParsing().parse_prompt_functions([data])
