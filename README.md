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

## Contents

- [Collecting Twitter Data](#collecting-twitter-data)
- [Input and Output](#input-and-output)
- [Installation](#installation)
- [Usage](#usage)
- [About tidy_tweet](#about-tidy_tweet)

## Collecting Twitter data

If you do not have a preferred Twitter collection tool already, we recommend [Twarc](https://github.com/DocNow/twarc/). 
tidy_tweet is designed to work directly with Twarc output. Other collection methods may work with tidy_tweet as long
as they output the API result from Twitter with minimal alteration (see [Input and Output](#input-and-output)), however 
at this time we do not have the resources to support Twitter data outputs from tools other than Twarc. 

## Input and Output

### Input: Twitter results pages

tidy_tweet takes as input a series of JSON/dict objects, each object of which is a page of Twitter API v2 search or 
timeline results. Typically, this will be a JSON file such as those output by `twarc2 search`.

JSON files with multiple pages of results are expected to be newline-delimited, with each line being a distinct results
page object, and no commas between top-level objects.

### Output: Sqlite database of tweets and metadata

After processing your Twitter results pages with tidy_tweet (see [Usage](#usage)), you will have an 
[SQLite](https://sqlite.org/index.html) database file at the location you specified.

Database schema will be published here as soon as the initial schema is finalised.

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
