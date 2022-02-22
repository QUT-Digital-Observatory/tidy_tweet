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
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Feedback and Contributions](#feedback-and-contributions)
- [About tidy_tweet](#about-tidy_tweet)

## Collecting Twitter data

If you do not have a preferred Twitter collection tool already, we recommend [Twarc][twarc]. 
tidy_tweet is designed to work directly with Twarc output. Other collection methods may work with tidy_tweet as long
as they output the API result from Twitter with minimal alteration (see [Input and Output](#input-and-output)), however 
at this time we do not have the resources to support Twitter data outputs from tools other than Twarc. 

## Input and Output

### Input: Twitter tweet results pages

tidy_tweet takes as input a series of JSON/dict objects, each object of which is a page of Twitter API v2 search or 
timeline results. Typically, this will be a JSON file such as those output by `twarc2 search`. At present, API endpoints
oriented around things other than tweets, such as the `liking-users` endpoint, are not properly supported, though we 
hope to support them in future.

JSON files with multiple pages of results are expected to be newline-delimited, with each line being a distinct results
page object, and no commas between top-level objects.

### Output: Sqlite database of tweets and metadata

After processing your Twitter results pages with tidy_tweet (see [Usage](#usage)), you will have an 
[SQLite][sqlite] database file at the location you specified.

Database schema will be published here as soon as the initial schema is finalised.

## Prerequisites

- Python 3.8+
- A command line shell/terminal, such as bash, Mac Terminal, Git Bash, Anaconda Prompt, etc

This tool requires Python 3.8 or later, the instructions assume you already have Python installed. If you haven't
installed Python before, you might find [Python for Beginners][python_beginners] helpful - note that tidy_tweet is a
command line application, you don't need to write any Python code to use it (although you can if you want to), you just
need to be able to run Python code!

The instructions assume sufficient familiarity with using a command line to change directories, list files and find
their locations, and execute commands. If you are new to the command line or want a refresher, there are some good
lessons from [Software Carpentry][sc_unix_intro] and the [Programming Historian][ph_bash_intro].

The instructions assume you are working in a suitable Python
[virtual environment][py_venv]. RealPython has a relatively straightforward
[primer on virtual environments][realpy_venv] if you are new to the concept. If you installed Python with
Anaconda/conda, you will want to manage your virtual environments through [Anaconda][anaconda_venv]/[conda][conda_venv]
as well. If you have a virtual environment already set up for using [Twarc][twarc], you can install tidy_tweet in that
same environment.

## Installation

tidy_tweet is a Python package and can be installed with pip.

1. Ensure you are using an appropriate Python or Anaconda environment (see [Prerequisites](#prerequisites))

2. Install tidy_tweet and its requirements by running:

   ```bash
   python -m pip install tidy_tweet
   ```

3. Run the following to check that your environment is ready to run tidy_tweet:
   
    ```bash
   tidy_tweet --help
   ```


If you wish to install a specific version of tidy_tweet, for example to replicate past results, you can specify the 
desired version when installing with pip, for example to install tidy_tweet version 1.0.1 (which does not currently
exist):

```bash
python -m pip install tidy-tweet==1.0.1 
```

## Usage

tidy_tweet may be used either as a [command line application](#command-line-interface) or as
a [Python library](#python-library). The command line interface (CLI) is recommended for general use and is intended to
be more straightforward to use. The Python library interface is designed for use cases such as integrating tidy_tweet
usage into other tools, scripts, and notebooks.

### Command line interface

After [installing tidy_tweet](#installation), you should be able to run `tidy_tweet` as a command line application:

```bash
tidy_tweet --help
```

Running the above will show you a summary of how to use the tidy_tweet command line interface (CLI). The 
tidy_tweet CLI expects you to provide specific arguments in a specific order, as follows:

```bash
tidy_tweet DATABASE JSON_FILE
```

**DATABASE**: This is the filename where you want to save the tidied data as a database. As this is an [SQLite][sqlite]
database, it is conventional for the filename to end in ".db". Example: `my_dataset.db`

**JSON_FILE**: This is the file of tweets you wish to tidy into the database. For more information,
see [Input and Output](#input-and-output) Example: `my_search_results.json`

Example:

```bash
tidy_tweet tree_search_2022-02-22.db tree_search_2022-02-22.json
```

#### Loading multiple JSON files into a database

tidy_tweet can accept more than one JSON file at a time. If you have multiple JSON files, for example resulting
from different search terms or Twitter accounts, you can list them all in a single `tidy_tweet` command:

```bash
tidy_tweet DATABASE JSON_FILE_1 JSON_FILE_2 JSON_FILE_3
```

For example:

```bash
tidy_tweet tree_searches_2022-02-22.db pine_tree_2022-02-22.json eucalypt_2022-02-22.json jacaranda_2022-02-22.json
```

At present, there is no metadata to tell what data came from which file, but we plan to fix this soon!

### Python library

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

## Feedback and contributions

We appreciate all feedback and contributions!

Found an issue with tidy_tweet? [Find out how to let us know](contributing.md#filing-an-issue)

Interested in contributing? Find out more in our [contributing.md](contributing.md)

## Acknowledgements

Some of this documentation is copied from [Gab Tidy Data](https://github.com/QUT-Digital-Observatory/gab_tidy_data), 
and much of the structure and functionality is also modelled on gab_tidy_data, which was our initial foray into
developing a tool like this.

## About tidy_tweet

Tidy_tweet is created and maintained by the [QUT Digital Observatory](https://www.qut.edu.au/digital-observatory) and
is open-sourced under an MIT license. We welcome contributions and feedback!

A DOI and citation information will be added in future.


[twarc]: https://github.com/DocNow/twarc/
[sqlite]: https://sqlite.org/index.html
[python_beginners]: https://www.python.org/about/gettingstarted/
[sc_unix_intro]: https://swcarpentry.github.io/shell-novice/
[ph_bash_intro]: https://programminghistorian.org/en/lessons/intro-to-bash
[py_venv]: https://docs.python.org/3/tutorial/venv.html
[realpy_venv]: https://realpython.com/python-virtual-environments-a-primer/
[conda_venv]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
[anaconda_venv]: https://docs.anaconda.com/anaconda/navigator/getting-started/#navigator-managing-environments

