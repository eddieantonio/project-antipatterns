import pytest  # type: ignore

from .message_patterns import PATTERNS, MessagePattern


@pytest.mark.parametrize("pattern", PATTERNS)
def test_signature_should_match(pattern: MessagePattern):
    "Ensure each pattern matches its given signature"
    assert pattern.match(pattern.signature)


def test_regression_cant_resolve_variable():
    m = MessagePattern.match_all("cannot find symbol - variable Charecter")
    assert m is not None
    assert m.message_id == "compiler.err.cant.resolve[variable]"


def test_regression_incompatible_types():
    """
    Old enough versions of javac could produce the error message:

        incompatible types

    with nothing more. So this error message should match too.

    See: https://github.com/openjdk/jdk/blob/jdk7-b24/langtools/src/share/classes/com/sun/tools/javac/resources/compiler.properties#L923
    """
    m = MessagePattern.match_all("incompatible types")
    assert m is not None
    assert m.message_id == "compiler.err.prob.found.req"

    # Don't match this:
    m = MessagePattern.match_all("incompatible typesies")
    assert m is None


def test_regression_unexpected_type():
    """
    At some point, the initial spacing changed with this one.
    """
    m1 = MessagePattern.match_all(
        """unexpected type
  required: variable
  found:    value"""
    )
    assert m1 is not None

    m2 = MessagePattern.match_all(
        """unexpected type
required: variable
found   : value"""
    )
    assert m2 is not None

    assert m1.message_id == "compiler.err.type.found.req"
