import sqlite3
import json
from typing import Dict, Any, List, Union
from os import PathLike
import tidy_tweet.tweet_mapping as mapping
from logging import basicConfig, getLogger
from tidy_tweet.utilities import add_mappings

basicConfig()

logger = getLogger(__name__)


def initialise_sqlite(db_name: Union[str, PathLike]):
    with sqlite3.connect(db_name) as db:
        cursor = db.cursor()
        for tbl_stmt in mapping.create_table_statements:
            cursor.execute(tbl_stmt)

        # ".tables" only works in the sqlite shell!
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        created_tables = cursor.fetchall()
        logger.debug("Created database tables: " + str(created_tables))
        assert len(created_tables) == len(mapping.create_table_statements)
        logger.info("The database schema has been initialised")


def load_twarc_json_to_sqlite(
    filename: Union[str, PathLike], db_name: Union[str, PathLike]
):
    with sqlite3.connect(db_name) as db, open(filename, "r") as json_fh:
        for page in json_fh:
            page_json = json.loads(page)

            mappings = {}

            # Includes
            if "media" in page_json["includes"]:
                add_mappings(
                    mappings, mapping.map_media(page_json["includes"]["media"])
                )

            for user in page_json["includes"]["users"]:
                add_mappings(mappings, mapping.map_user(user))

            for tweet in page_json["includes"]["tweets"]:
                add_mappings(mappings, mapping.map_tweet(tweet, False))

            # Data
            for tweet in page_json["data"]:
                add_mappings(mappings, mapping.map_tweet(tweet, True))

            # TODO: doing this all in one big go isn't great
            for table, table_mappings in mappings.items():
                if len(table_mappings) == 0:
                    continue
                elif not isinstance(table_mappings, list):
                    db.execute(mapping.sql_by_table[table]["insert"], table_mappings)
                else:
                    db.executemany(
                        mapping.sql_by_table[table]["insert"], table_mappings
                    )
