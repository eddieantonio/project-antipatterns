#!/usr/bin/env python3

"""
Enriches the error message database by adding functions:
    - sanitize_message(text)    -- get sanitized error message
    - javac_name(text)          -- get javac name for error message

And a derived table:

    sanitized_messages(text, javac_name, sanitized_message)

Top errors can be can be retrieved as thus:

    SELECT sanitized_text, COUNT(sanitized_text)
      FROM messages JOIN sanitized_messages USING (text)
     GROUP BY sanitized_text
     ORDER BY COUNT(sanitized_text) DESC;

Top first error messages can be retrieved as thus:

    SELECT sanitized_text, COUNT(sanitized_text)
      FROM messages JOIN sanitized_messages USING (text)
     WHERE rank = 1
     GROUP BY sanitized_text
     ORDER BY COUNT(sanitized_text) DESC;
"""

import sqlite3
from functools import lru_cache

from java_error_messages import match_message

# Cache match_message() to avoid too many re lookups.
match_message = lru_cache(1024)(match_message)


def register_helpers(conn: sqlite3.Connection):
    def sanitize_message(text) -> str:
        "Return my santized version of the error message"
        return match_message(text).sanitized_message

    def javac_name(text) -> str | None:
        "Returns javac's internal name for the message -- note: many message categories overlap"
        return match_message(text).javac_name

    def parameterized_javac_name(text) -> str | None:
        "Returns javac's internal name for the message, with disambiguation"
        return match_message(text).message_id

    conn.create_function("sanitize_message", 1, sanitize_message)
    conn.create_function("javac_name", 1, javac_name)
    conn.create_function("parameterized_javac_name", 1, parameterized_javac_name)


if __name__ == "__main__":
    import sys

    try:
        db_path = sys.argv[1]
    except IndexError:
        print(
            "error: please provide a path to the database you wish to enrich",
            file=sys.stderr,
        )
        sys.exit(65)

    conn = sqlite3.connect(db_path)
    register_helpers(conn)

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sanitized_messages
            AS SELECT text,
                      javac_name(text) as javac_name,
                      sanitize_message(text) as sanitized_text
                 FROM (SELECT DISTINCT text from messages)
            """
        )
        # TODO: primary key text?
        conn.execute(
            """
            CREATE UNIQUE INDEX text_idx ON sanitized_messages(text);
            """
        )
