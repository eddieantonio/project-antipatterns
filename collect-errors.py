#!/usr/bin/env python3

"""
Collect raw error messages from Blackbox Mini and insert them into several
databases. Use combine-databases.py later to combine them all into one.
"""

import sqlite3
import logging
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import blackbox_mini
from decode_escapes import decode_escapes
from database import SCHEMA


DATASET_ROOT = Path("/data/mini/")

logger = logging.getLogger(__name__)


def main():
    """
    Collect all error messages from Blackbox mini.
    Will create SEVERAL .sqlite3 database called:

        errors-{slice-date}.sqlite3

    Each slice will be computed in a separate process. I have hard-coded the
    number of processors on the machine I want to run this on.
    """

    slices = blackbox_mini.slices()

    # I looked at htop on white and found this many processors:
    n_processors = 24
    # Neil was only using 1/4 of the cores, so :/
    executor = ProcessPoolExecutor(max_workers=n_processors // 4)
    executor.map(process_entire_slice, slices)


def process_entire_slice(slice_root: Path):
    """
    Given a slice path, will commit all error messages found to a database.
    """
    date = slice_root.name[len("srcml-"):]
    assert len(date) > 0

    logger.debug("Starting slice %s (%s)", date, slice_root)
    collect_errors_from_slice(
        slice_root=slice_root,
        database_path=f"errors-{date}.sqlite3"
    )


def collect_errors_from_slice(*, database_path: Path, slice_root: Path):
    """
    Collect all the error messages from one slice of Blackbox Mini, and stuff
    them into the given database name.

    Messages are committed in batches. Each batch is one project from within
    the slice.
    """
    assert slice_root.match("srcml-*")

    conn = sqlite3.connect(database_path)
    try:
        init_db(conn)
        for project in generate_all_project_paths(slice_root):
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
    logging.basicConfig(filename='data-collection.log', level=logging.DEBUG)
    main()
