import sqlite3
import json
from typing import Union, Mapping
from os import PathLike
import tidy_tweet.tweet_mapping as mapping
from logging import getLogger
from tidy_tweet.utilities import add_mappings

logger = getLogger(__name__)


def _load_page_object(
    file_name: str, page_json: Mapping, connection: sqlite3.Connection
):
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

    # Metadata
    logger.debug("Processing metadata section of page")
    twitter_metadata = page_json.get("meta", {})
    twarc_metadata = page_json.get("__twarc", {})
    # Write this first so we can get the page id
    db.execute(
        mapping.sql_by_table["results_page"]["insert"],
        mapping.map_page_metadata(file_name, twitter_metadata, twarc_metadata),
    )
    page_info = (file_name, db.lastrowid)

    # Includes
    logger.debug("Processing includes section of page")
    if "media" in page_json["includes"]:
        add_mappings(mappings, mapping.map_media(page_json["includes"]["media"]))

    for user in page_json["includes"].get("users", []):
        add_mappings(mappings, mapping.map_user(user, *page_info))

    for tweet in page_json["includes"].get("tweets", []):
        add_mappings(mappings, mapping.map_tweet(tweet, False, *page_info))

    # Data
    logger.debug("Processing data section of page")

    #  - Some endpoints will return responses without data (for example if all
    #    of the tweets in a hydration call are no longer available)
    #  - For most endpoints this will be a list of tweets if present,
    #    otherwise for the sample and filter endpoints this will be a
    #    single tweet object in the data key.
    tweet_or_tweets = page_json.get("data", [])

    if isinstance(tweet_or_tweets, list):
        tweets = tweet_or_tweets
    elif isinstance(tweet_or_tweets, dict):
        tweets = [tweet_or_tweets]

    for tweet in tweets:
        add_mappings(mappings, mapping.map_tweet(tweet, True, *page_info))

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
) -> int:
    """
    Parses a json/jsonl file produced by a Twarc search and loads the Twitter data into
    a tidied, relational format in an sqlite database.

    Before calling this function, the database should already have been initialised with
    the `tidy_tweet.initialise_sqlite()` function.

    :param filename: The path to a json/jsonl file of Twitter data. The file is expected
    to be in the format of the results of a Twarc search.
    :param db_name: The path to an existing sqlite database to load the data into
    :return: The number of pages of Twitter results loaded in this file
    """
    with open(filename, "r") as json_fh, sqlite3.connect(db_name) as connection:
        logger.info(f"Loading {filename} into {db_name}")

        page_num = 0
        for page in json_fh:
            page_num = page_num + 1
            logger.info(f"Processing page {page_num} of {filename}")
            page_json = json.loads(page)
            try:
                _load_page_object(str(filename), page_json, connection)
            except Exception as e:
                raise PageParsingError(filename, page_num) from e

        logger.info(f"All {page_num} pages of {filename} processed")
    return page_num


class PageParsingError(Exception):
    file_name: str
    page_number: int

    def __init__(self, file_name: str, page_number: int, *args):
        self.file_name = file_name
        self.page_number = page_number

        super().__init__(*args)

    def __str__(self):
        return "tidy_tweet encountered an error while parsing page " \
               f"{self.page_number} of file {self.file_name}"

