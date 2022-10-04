# Project anti-patterns data collection scripts

Here are most of the scripts I used to collect (and maybe even analyze)
data for project anti-patterns.

# What's here?

    .
    ├── blackbox_mini.py          -- library for working with Blackbox Mini
    ├── collect-errors.py         -- collect error message from Blackbox Mini
    ├── combine-databases.py      -- combine Blackbox Mini databases
    ├── database.py               -- library for working with local database
    ├── decode_escapes.py         -- decodes escapes in error messages
    ├── enrich-database.py        -- augments the database of messages
    ├── java_error_messages/      -- library for working with javac messages
    ├── top-first-messages.sql    -- query for top first messages
    └── top-messages.sql          -- query for top messages

If the documentation is lacking or inaccurate, feel free to
[bug me](https://github.com/eddieantonio/project-antipatterns/issues).

# How to collect data

    python3 collect-errors.py &&\
        python3 combine-databases.py &&\
        python3 enrich-database.py errors.sqlite3

Better documentation coming soon!

# System requirements

To run the scripts, you must have:

 - Python 3.8+

Note: some of these scripts are meant to run on the BlueJ's machine,
which at time of writing, only has Python 3.8 and not much else. So
you'll see code that relies heavily on the Python standard library here.

To run tests and quality assurance stuff, you will need:

 - [Poetry](https://python-poetry.org/)

# Installing

    poetry install --with=dev

# Testing

Check static typing:

    poetry run mypy .

Run test cases:

    poetry run pytest

# See also

 - [`javac` Error Explorer](https://github.com/eddieantonio/javac-error-explorer) 
