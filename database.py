"""
Shared utilties for the database.
"""

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages(
    srcml_path TEXT,
    version INT,
    rank INT,
    start TEXT,
    end TEXT,
    text TEXT
);
"""
