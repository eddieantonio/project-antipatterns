"""
Decoding escapes in Python, the right way.

Do not use unicode-escape.
"""

import codecs
import re

# (sigh)
# https://stackoverflow.com/a/24519338
ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)
