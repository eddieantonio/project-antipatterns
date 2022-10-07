import sqlite3
import sys
from itertools import count
from random import choice, randint, sample

from error_database import Database

version = count(start=1)
project = count(start=1)
source_file = count(start=1)


def create_slice(slice_name: str):
    def generate_errors_for_project(project_id: int):
        for _ in range(randint(1, 8)):
            yield from generate_errors(project_id, next(source_file))

    def generate_errors(project_id: int, source_id: int):
        for rank in range(1, randint(2, 10)):
            yield (
                f"/data/mini/srcml-{slice_name}/project-{project_id}/src-{source_id}.xml",
                next(version),
                rank,
                "<unknown>",
                "<unknown>",
                random_error_message(),
            )

    def random_error_message():
        return choice(
            [
                "cannot find symbol - class system",
                "not a statement",
                "';' expected",
            ]
        )

    conn = sqlite3.connect(f"errors-{slice_name}.sqlite3")

    db = Database(conn)
    db.apply_schema()

    for _ in range(randint(1, 1000)):
        db.insert_batch(generate_errors_for_project(next(project)))
    db.populate_sources()


def all_possible_slices():
    for year in range(2015, 2022):
        for month_zero in range(12):
            month = month_zero + 1
            yield f"{year}-{month}"


if __name__ == "__main__":
    slices = sample(list(all_possible_slices()), 6)
    for slice_name in slices:
        create_slice(slice_name)
