# tidy_tweet

This is *extremely preliminary*. Not all entities/fields are loaded. Library structure
will change.

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
