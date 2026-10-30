"""Unit tests for the load_json function."""

import json
from pathlib import Path
from src.__main__ import load_json
import pytest


def test_load_json_valid(tmp_path: Path) -> None:
    contain = [{"prompt": "greet john"}]

    file = tmp_path / "test.json"
    file.write_text(json.dumps(contain))

    result = load_json(str(file))

    assert result == contain


def test_load_json_file_not_found() -> None:
    with pytest.raises(SystemExit):
        load_json("files_not_exist.json")


def test_load_json_break(tmp_path: Path) -> None:

    break_file = tmp_path / "test.json"
    break_file.write_text("this is not a json {{")

    with pytest.raises(SystemExit):
        load_json(str(break_file))


def test_load_json_directoy(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        load_json(str(tmp_path))


def test_load_json_file_empty(tmp_path: Path) -> None:

    break_file = tmp_path / "test.json"
    break_file.write_text("")

    with pytest.raises(SystemExit):
        load_json(str(break_file))


def test_load_json_permission(tmp_path: Path) -> None:
    contain = [{"prompt": "greet john"}]

    file = tmp_path / "test.json"
    file.write_text(json.dumps(contain))

    file.chmod(0o000)
    with pytest.raises(SystemExit):
        load_json(str(file))
