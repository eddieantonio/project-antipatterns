import pytest  # type: ignore

from .message_patterns import PATTERNS, MessagePattern


@pytest.mark.parametrize("pattern", PATTERNS)
def test_signature_should_match(pattern: MessagePattern):
    "Ensure each pattern matches its given signature"
    assert pattern.match(pattern.signature)
