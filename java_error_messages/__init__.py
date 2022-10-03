"""
Utilities for dealing with error messages from javac.
"""

from typing import Literal, NamedTuple

from .message_patterns import MessagePattern
from .simple_error_messages import SIMPLE_ERROR_MESSAGES


class MatchResult(NamedTuple):
    kind: Literal["no_match", "match_simple", "match_pattern"]
    javac_name: str | None
    sanitized_message: str


def match_message(message: str) -> MatchResult:
    """
    Attempts to match any known error message.
    """

    # Do hash table look up first -- faster than trying a bunch of regexes.
    if name := SIMPLE_ERROR_MESSAGES.get(message):
        return MatchResult(
            kind="match_simple", javac_name=name, sanitized_message=message
        )
    elif pattern := MessagePattern.match_all(message):
        return MatchResult(
            kind="match_pattern",
            javac_name=pattern.javac_name,
            sanitized_message=pattern.signature,
        )
    else:
        return MatchResult(kind="no_match", javac_name=None, sanitized_message=message)
