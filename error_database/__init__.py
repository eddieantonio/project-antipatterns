"""
Shared utilties for the database.
"""

import sqlite3
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Iterator

from java_error_messages import match_message

SCHEMA = """
CREATE TABLE all_messages(
    srcml_path      TEXT,
    version         INT NOT NULL,
    rank            INT NOT NULL,
    start           TEXT NOT NULL,
    end             TEXT NOT NULL,
    text            TEXT NOT NULL,

    PRIMARY KEY (srcml_path, version, rank)
);

CREATE TABLE source(
    srcml_path      TEXT PRIMARY KEY,
    slice           TEXT NOT NULL,
    project_id      INT NOT NULL,
    source_file_id  INT NOT NULL
);

CREATE TABLE sanitized_messages(
    text            TEXT PRIMARY KEY,
    javac_name      TEXT,
    sanitized_text  TEXT NOT NULL
);

CREATE VIEW first_messages(srcml_path, version, start, end, text)
AS SELECT srcml_path, version, start, end, text
     FROM all_messages
    WHERE rank = 1;
"""


Message = tuple[str, int, int, str, str, str]


class Database:
    """
    Provides an abstracted mechanism to the error message database.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._register_helpers()

    def apply_schema(self) -> None:
        """
        Make sure all tables and views are created.
        """
        with self.conn:
            self.conn.executescript(SCHEMA)

    def combine_with(self, db_path: Path):
        """
        Get all message and source data from the given database. It is assumed that the
        given database contains one or more entire slices, and those slices are not
        already in the existing database.
        """
        # Based on https://stackoverflow.com/a/11089277
        self.conn.executescript(
            f"""
            ATTACH '{db_path}' as slice;
            BEGIN;
            INSERT INTO all_messages
                SELECT * FROM slice.all_messages;
            INSERT INTO source
                SELECT * FROM slice.source;
            COMMIT;
            DETACH slice;
            """
        )

    def insert_batch(self, messages: Iterator[Message]):
        """
        Inserts a batch of error messages into the database. All messages are inserted
        in one transaction. It's recommened to insert to insert an entire project's
        worth at a time, so that if anything fails, it can be localized to one specific
        project.
        """
        with self.conn:
            self.conn.executemany(
                """
                INSERT INTO all_messages (srcml_path, version, rank, start, end, text)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                messages,
            )

    def populate_sanitized_messages(self) -> None:
        """
        Generates sanitized messages from all messages.
        """
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO sanitized_messages (text, javac_name, sanitized_text)
                SELECT text,
                       javac_name(text) as javac_name,
                       sanitize_message(text) as sanitized_text
                  FROM (SELECT DISTINCT text from all_messages)
                """
            )

    def populate_sources(self) -> None:
        """
        Generates sources from all messages.
        """
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO source(srcml_path, slice, project_id, source_file_id)
                SELECT srcml_path,
                          slice_name(srcml_path) as slice,
                          project_id(srcml_path) as project_id,
                          source_id(srcml_path) as source_file_id
                 FROM (SELECT DISTINCT srcml_path FROM all_messages)
                """
            )

    def _register_helpers(self) -> None:
        self.conn.create_function("sanitize_message", 1, sanitize_message)
        self.conn.create_function("javac_name", 1, javac_name)
        self.conn.create_function("slice_name", 1, slice_name)
        self.conn.create_function("project_id", 1, project_id)
        self.conn.create_function("source_id", 1, source_id)


# Cache match_message() to avoid too many re lookups.
match_message = lru_cache(1024)(match_message)


def sanitize_message(text: str) -> str:
    return match_message(text).sanitized_message


def javac_name(text: str) -> str | None:
    return match_message(text).javac_name


def slice_name(text: str) -> str:
    return parse_path(PurePosixPath(text))[0]


def project_id(text: str) -> int:
    return parse_path(PurePosixPath(text))[1]


def source_id(text: str) -> int:
    return parse_path(PurePosixPath(text))[2]


@lru_cache(128)
def parse_path(path: PurePosixPath):
    *_, slice_dir, project_dir, xml_name = path.parts
    assert xml_name.endswith(".xml")
    slice_name = slice_dir.removeprefix("srcml-")
    project_id = project_dir.removeprefix("project-")
    source_id = path.stem.removeprefix("src-")

    return slice_name, int(project_id), int(source_id)
