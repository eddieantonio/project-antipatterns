#!/usr/bin/env python3

"""
Combine all the per-slice errors-*.sqlite3 databases into errors.sqlite3
"""

import sqlite3
from pathlib import Path

from database import SCHEMA

dbs = list(Path(".").glob("errors-*.sqlite3"))
assert len(dbs) > 0

# Initialize the combined DB with the schema first:
conn = sqlite3.connect("errors.sqlite3")
with conn:
    conn.executescript(SCHEMA)


# Based on https://stackoverflow.com/a/11089277
for db_path in dbs:
    conn.executescript(f"""
        ATTACH '{db_path}' as slice;
        BEGIN;
        INSERT INTO messages
            SELECT * FROM slice.messages;
        COMMIT;
        DETACH slice;
    """)
