# tidy_tweet

Tidies Twitter json collected with Twarc into relational tables.

The resulting SQLite database is ideal for importing into analytical tools, or for using as a datasource for a
programmatic analytical workflow that is more efficient than working directly from the raw JSON. However, we always
recommend retaining the raw JSON data - think of tidy_tweet and its resulting databases as the first step of data
pre-processing, rather than as the original/raw data for your project.

*WARNING* - tidy_tweet is still released in a preliminary version, not all data fields are loaded into the database,
and we can't guarantee no breaking changes either of library interface or database schema before 1.0 release. Most 
notably, the database schema will have a significant change to allow multiple JSON files to be loaded into the same
database file.

## Installation

tidy_tweet is a Python package and can be installed with pip.

Short version of installation instructions:

```bash
pip install tidy-tweet
```

## Usage

A command-line interface (CLI) is planned for the future, but is not yet implemented.

### Using tidy_tweet as a Python library

Here is an example using the test data file included with tidy_tweet:

```python
from tidy_tweet import initialise_sqlite, load_twarc_json_to_sqlite
import sqlite3

initialise_sqlite('ObservatoryTeam.db')
load_twarc_json_to_sqlite('tests/data/ObservatoryTeam.jsonl', 'ObservatoryTeam.db')

with sqlite3.connect('ObservatoryTeam.db') as connection:
    db = connection.cursor()

    db.execute("select count(*) from tweet")

    print(f"There are {db.fetchone()[0]} tweets in the database!")
```

## About tidy_tweet

Tidy_tweet is created and maintained by the [QUT Digital Observatory](https://www.qut.edu.au/digital-observatory) and
is open-sourced under an MIT license. We welcome contributions and feedback!

A DOI and citation information will be added in future.
