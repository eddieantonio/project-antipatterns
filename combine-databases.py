#!/usr/bin/env python3

"""
Combine all the per-slice errors-*.sqlite3 databases into errors.sqlite3
"""

import sqlite3
from pathlib import Path

from error_database import Database

dbs = list(Path(".").glob("errors-*.sqlite3"))
assert len(dbs) > 0

# Initialize the combined DB with the schema first:
conn = sqlite3.connect("errors.sqlite3")
db = Database(conn)
db.apply_schema()

# Now combine dbs, one by one.
for other_db in dbs:
    db.combine_with(other_db)
