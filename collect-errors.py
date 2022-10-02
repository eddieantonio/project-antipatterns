"""
Collect raw error messages from Blackbox mini.
"""

import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from decode_escapes import decode_escapes


DATASET_ROOT = Path("/data/mini/srcml-2013-06")

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
    from itertools import islice
    conn = sqlite3.connect("errors.sqlite3")
    try:
        init_db(conn)
        insert_batch(conn, islice(generate_all_compiler_errors(), 100))
    finally:
        conn.close()


def generate_all_compiler_errors():
    srcmls = DATASET_ROOT.glob("**/src-*.xml")
    for srcml_path in srcmls:
        yield from find_compiler_errors_in_file(srcml_path)


def find_compiler_errors_in_file(srcml_path: Path):
    try:
        root = ET.parse(srcml_path).getroot()
    except ET.ParseError as e:
        logger.exception("While parsing %s", srcml_path)
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
    with conn:
        conn.executescript(SCHEMA)


def insert_batch(conn, messages):
    with conn:
        conn.executemany(
            """
            INSERT INTO messages (srcml_path, version, rank, start, end, text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            messages
        )

def convert_to_int_if_not_none(x):
    if x is not None:
        return int(x)
    return None


if __name__ == '__main__':
    logging.basicConfig()
    main()
