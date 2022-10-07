#!/usr/bin/env python3

"""
Enriches the error message database by adding functions:
    - sanitize_message(text)    -- get sanitized error message
    - javac_name(text)          -- get javac name for error message

And a derived table:

    sanitized_messages(text, javac_name, sanitized_message)

Top errors can be can be retrieved as thus:

    SELECT sanitized_text, COUNT(sanitized_text)
      FROM all_messages JOIN sanitized_messages USING (text)
     GROUP BY sanitized_text
     ORDER BY COUNT(sanitized_text) DESC;

Top first error messages can be retrieved as thus:

    SELECT sanitized_text, COUNT(sanitized_text)
      FROM first_messages JOIN sanitized_messages USING (text)
     GROUP BY sanitized_text
     ORDER BY COUNT(sanitized_text) DESC;
"""

import sqlite3

from error_database import Database

if __name__ == "__main__":
    import sys

    try:
        db_path = sys.argv[1]
    except IndexError:
        db_path = "errors.sqlite3"

    conn = sqlite3.connect(db_path)
    db = Database(conn)
    db.populate_sanitized_messages()
    conn.close()
