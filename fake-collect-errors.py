def fake_main():
    conn = sqlite3.connect("temp-errors.sqlite3")
    db = Database(conn)

    try:
        db.apply_schema()
        db.insert_batch(
            [
                (
                    "/data/mini/srcml-2013-06/project-1/src-1.xml",
                    1,
                    1,
                    "1:1",
                    "1:72",
                    "cannot find symbol - class system",
                ),
                (
                    "/data/mini/srcml-2013-06/project-1/src-1.xml",
                    1,
                    2,
                    "2:1",
                    "2:72",
                    "not a statement",
                ),
            ]
        )
        db.populate_sources()
    finally:
        conn.close()
