"""Tests unitaires des règles de décodage contraint des nombres."""

from src.generator import rules_number_parameters


def test_number_valid() -> None:
    assert rules_number_parameters("12") is True


def test_negatif_decimal() -> None:
    assert rules_number_parameters("-3.5") is True


def test_number_number_end() -> None:
    assert rules_number_parameters("12,") is True


def test_dubble_point() -> None:
    assert rules_number_parameters("1.2.3") is False


def test_begin_point() -> None:
    assert rules_number_parameters(".5") is False


def test_middle_line() -> None:
    assert rules_number_parameters("1-2") is False


def test_letter() -> None:
    assert rules_number_parameters("abc") is False


def test_comma() -> None:
    assert rules_number_parameters(",") is False


def test_after_comma() -> None:
    assert rules_number_parameters("5,000") is False
