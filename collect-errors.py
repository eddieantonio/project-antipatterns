"""
Collect raw error messages from Blackbox mini.
"""

import sqlite3
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from decode_escapes import decode_escapes


DATASET_ROOT = Path("/data/mini/srcml-2013-06")

logger = logging.getLogger(__name__)


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


def convert_to_int_if_not_none(x):
    if x is not None:
        return int(x)
    return None


if __name__ == '__main__':
    from itertools import islice
    logging.basicConfig()

    conn = sqlite3.connect("errors.sqlite3")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS messages(
        srcml_path TEXT,
        version INT,
        rank INT,
        start TEXT,
        end TEXT,
        text TEXT
    );
    """)
    conn.executemany(
        """
        INSERT INTO messages (srcml_path, version, rank, start, end, text)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        generate_all_compiler_errors()
    )
    conn.commit()
    conn.close()