import pytest  # type: ignore

from .message_patterns import PATTERNS, MessagePattern


@pytest.mark.parametrize("pattern", PATTERNS)
def test_signature_should_match(pattern: MessagePattern):
    "Ensure each pattern matches its given signature"
    assert pattern.match(pattern.signature)


def test_regressions():
    m = MessagePattern.match_all("cannot find symbol - variable Charecter")
    assert m is not None
    assert m.message_id == "compiler.err.cant.resolve[variable]"
