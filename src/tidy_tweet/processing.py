import sqlite3
import json
from typing import Union, Mapping
from os import PathLike
from pathlib import Path
import tidy_tweet.tweet_mapping as mapping
from logging import getLogger
from tidy_tweet.utilities import add_mappings

logger = getLogger(__name__)


def initialise_sqlite(
    db_name: Union[str, PathLike], allow_existing_database: bool = False
):
    """
    Creates and initialises an empty sqlite database for loading tweet data into.

    The database schema can be seen in the resulting sqlite .db file, or as a list
    of create table statements in `tidy_tweet.database_schema`

    :param db_name: File path to create a new database at. This is expected to not
    already exist.
    :param allow_existing_database: Only set this to True if you want to add the
    tidy_tweet tables to an existing database, such as one where you have other data
    pre-existing. This function expects the tidy_tweet tables to not already exist in
    the database. This behaviour, while possible, is not currently supported by
    tidy_tweet.
    """
    db_name = Path(db_name)

    if not allow_existing_database:
        assert not db_name.exists()

    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        for tbl_stmt in mapping.create_table_statements:
            cursor.execute(tbl_stmt)

        if not allow_existing_database:
            # ".tables" only works in the sqlite shell!
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            created_tables = cursor.fetchall()
            logger.debug("Created database tables: " + str(created_tables))
            assert len(created_tables) == len(mapping.create_table_statements)

        logger.info("The database schema has been initialised")


def _load_page_object(page_json: Mapping, connection: sqlite3.Connection):
    """
    Takes a page of twarc Twitter API results and loads it into the database.

    If using this function to parse Twitter data from an object direct from Twarc
    without saving the JSON Twarc output, we recommend you save the raw data Twarc json
    output by some other means.

    :param page_json: A dictionary (such as parsed json) of a single page of API results
    :param connection: An sqlite3 Connection object
    """
    db = connection.cursor()

    mappings = {}

    # Includes
    logger.debug("Processing includes section of page")
    if "media" in page_json["includes"]:
        add_mappings(mappings, mapping.map_media(page_json["includes"]["media"]))

    for user in page_json["includes"]["users"]:
        add_mappings(mappings, mapping.map_user(user))

    for tweet in page_json["includes"]["tweets"]:
        add_mappings(mappings, mapping.map_tweet(tweet, False))

    # Data
    logger.debug("Processing data section of page")
    for tweet in page_json["data"]:
        add_mappings(mappings, mapping.map_tweet(tweet, True))

    logger.debug(f"About to write to {len(mappings)} tables")
    for table, table_mappings in mappings.items():
        if len(table_mappings) == 0:
            continue
        elif not isinstance(table_mappings, list):
            db.execute(mapping.sql_by_table[table]["insert"], table_mappings)
        else:
            db.executemany(mapping.sql_by_table[table]["insert"], table_mappings)

    logger.debug("Finished writing page to database.")


def load_twarc_json_to_sqlite(
    filename: Union[str, PathLike], db_name: Union[str, PathLike]
):
    """
    Parses a json/jsonl file produced by a Twarc search and loads the Twitter data into
    a tidied, relational format in an sqlite database.

    Before calling this function, the database should already have been initialised with
    the `tidy_tweet.initialise_sqlite()` function.

    :param filename: The path to a json/jsonl file of Twitter data. The file is expected
    to be in the format of the results of a Twarc search.
    :param db_name: The path to an existing sqlite database to load the data into
    """
    with open(filename, "r") as json_fh, sqlite3.connect(db_name) as connection:
        logger.info(f"Loading {filename} into {db_name}")

        page_num = 0
        for page in json_fh:
            page_num = page_num + 1
            logger.info(f"Processing page {page_num} of {filename}")
            page_json = json.loads(page)
            _load_page_object(page_json, connection)

        logger.info(f"All {page_num} pages of {filename} processed")
