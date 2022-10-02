"""
Collect raw error messages from Blackbox Mini and insert them into the
database.
"""

import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from decode_escapes import decode_escapes


DATASET_ROOT = Path("/data/mini/")


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

logger = logging.getLogger(__name__)


def main():
    """
    Collect the first 100 messages from Blackbox mini.
    """
    from itertools import islice
    conn = sqlite3.connect("errors.sqlite3")
    try:
        init_db(conn)
        slice_root = next(iter(DATASET_ROOT.glob("srcml-*")))
        for project in islice(generate_all_project_paths(slice_root), 100):
            insert_batch(conn, generate_compiler_errors_for_project(project))
    finally:
        conn.close()


def generate_all_compiler_errors():
    """
    Yields every compiler error found within srcML files within in DATASET_ROOT
    (including subdirectories).
    """
    slices = DATASET_ROOT.glob("srcml-*")
    for slice_root in slices:
        for project in generate_all_project_paths(slice_root):
            yield from generate_compiler_errors_for_project(project)


def generate_compiler_errors_for_project(project_path: Path):
    assert project_path.match("project-*")
    for srcml_path in project_path.glob("src-*.xml"):
        yield from find_compiler_errors_in_file(srcml_path)


def generate_all_project_paths(slice_root: Path):
    """
    Given a path to the root of a slice, yields every project directory
    """
    assert slice_root.match("srcml-*")
    for entry in slice_root.glob("project-*"):
        if not entry.is_dir():
            continue
        yield entry


def find_compiler_errors_in_file(srcml_path: Path):
    """
    Given one srcML file, yields all compiler errors found within.

    If the file cannot be parsed, nothing is yielded and the exception is
    logged.
    """
    try:
        root = ET.parse(srcml_path).getroot()
    except ET.ParseError:
        logger.exception("Could not parse %s", srcml_path)
        return

    failed_compilations = root.findall('.//unit[@compile-success="false"]')
    if not failed_compilations:
        return

    for unit in failed_compilations:
        errors = unit.findall('./compile-error')
        for rank, error in enumerate(errors, start=1):
            yield (
                    str(srcml_path),
                    convert_to_int_if_not_none(unit.attrib.get('version')),
                    rank,
                    error.attrib.get('start'),
                    error.attrib.get('end'),
                    decode_escapes(error.text),
                )


def init_db(conn):
    """
    Initialize the database with the schema.
    """
    with conn:
        conn.executescript(SCHEMA)


def insert_batch(conn, messages):
    """
    Insert one batch of messages into the database.
    """
    with conn:
        conn.executemany(
            """
            INSERT INTO messages (srcml_path, version, rank, start, end, text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            messages
        )


def convert_to_int_if_not_none(x):
    """
    Utility to convert item to int if and only if the item is not None.
    """
    if x is not None:
        return int(x)
    return None


if __name__ == '__main__':
    logging.basicConfig()
    main()
