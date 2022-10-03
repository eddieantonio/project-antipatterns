import pytest

from . import match_message
from .simple_error_messages import SIMPLE_ERROR_MESSAGES


def test_matches_cannot_find_symbol():
    message = "cannot find symbol -   class Ratón"
    result = match_message(message)
    assert result.kind == "match_pattern"
    assert result.javac_name == "compiler.err.cant.resolve"
    assert result.sanitized_message != message


def test_matches_variable_already_defined():
    message = "variable i is already defined in method main(String[])"
    result = match_message(message)
    assert result.kind == "match_pattern"
    assert result.javac_name == "compiler.err.already.defined"
    assert result.sanitized_message != message


@pytest.mark.parametrize("message,name", SIMPLE_ERROR_MESSAGES.items())
def test_all_simple_messages(message: str, name: str):
    "Exhaustively test every simple message match."
    result = match_message(message)
    assert result.kind == "match_simple"
    assert result.javac_name == name
    assert result.sanitized_message == message


def test_unknown_message():
    "Test a message that we don't have a pattern for."
    message = "';' expected"
    result = match_message(message)
    assert result.kind == "no_match"
    assert result.javac_name is None
    assert result.sanitized_message == message
