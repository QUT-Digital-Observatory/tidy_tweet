import sqlite3
from pathlib import Path
from typing import Union
from os import PathLike
import tidy_tweet.tweet_mapping as mapping
from tidy_tweet._version import version as library_version
from logging import getLogger
from warnings import warn


logger = getLogger(__name__)


class SchemaVersionMismatchError(Exception):
    def __init__(self, library_schema_version, db_schema_version, db_name, *args):
        self.library_schema_version = library_schema_version
        self.db_schema_version = db_schema_version
        self.db_name = db_name
        super().__init__(*args)

    def message(self):
        msg = (
            f"Database file {self.db_name} is using tidy_tweet database schema "
            f"version {self.db_schema_version} but the version of tidy_tweet you "
            f"are running is using tidy_tweet database schema version "
            f"{self.db_schema_version}. These versions are not compatible. It is "
            f"recommended to reprocess all your json files into a fresh database."
        )
        return msg

    def __str__(self):
        return "Exception SchemaVersionMismatchError: " + self.message()


class LibraryVersionMismatchWarning(Warning):
    def __init__(self, this_library_version, db_library_version, db_name, *args):
        self.library_version = this_library_version
        self.db_library_version = db_library_version
        self.db_name = db_name
        super().__init__(*args)

    def message(self):
        msg = (
            f"Database file {self.db_name} contains data processed with tidy_tweet "
            f"version {self.db_library_version}, but the version of tidy_tweet you "
            f"are currently using is version {self.library_version}. This is not "
            f"necessarily incompatible, but if you notice any inconsistencies with "
            f"how the data is parsed, you may wish to reprocess all your json files "
            f"into a fresh and consistent database."
        )
        return msg

    def __str__(self):
        return "LibraryVersionMismatchWarning: " + self.message()


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

        # Initialise the schema related metadata first, otherwise if an
        # insert fails we end up with a schema version of null.
        cursor.executemany(
            mapping.sql_by_table["_metadata"]["insert"],
            mapping.map_tidy_tweet_metadata()["_metadata"],
        )

        if not allow_existing_database:
            # ".tables" only works in the sqlite shell!
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            created_tables = cursor.fetchall()
            logger.debug("Created database tables: " + str(created_tables))
            assert len(created_tables) == len(mapping.create_table_statements)

        logger.info("The database schema has been initialised")


def check_database_version(db_name):
    """
    Checks the given pre-existing database is valid for use with this version
    of the tidy_tweet library.

    Raises SchemaVersionMismatchError if there is a version mismatch in the database
    schema - mismatched database schemas are considered incompatible and file processing
    should be aborted.
    """
    logger.debug(f"Checking version compatibility of {db_name}...")
    conn = sqlite3.connect(db_name)
    with conn:
        db = conn.cursor()
        db.execute(
            """
            select metadata_value from _metadata
            where metadata_key='schema_version'
            """
        )
        result = db.fetchone() or []
        db_schema_version = None if len(result) == 0 else result[0]
        db.execute(
            """
            select metadata_value from _metadata
            where metadata_key='tidy_tweet_version'
            """
        )
        result = db.fetchone() or []
        db_library_version = None if len(result) == 0 else result[0]
    if db_schema_version != mapping.SCHEMA_VERSION:
        raise SchemaVersionMismatchError(
            mapping.SCHEMA_VERSION, db_schema_version, db_name
        )
    if db_library_version != library_version:
        warning = LibraryVersionMismatchWarning(
            library_version, db_library_version, db_name
        )
        logger.warning(warning.message())
        warn(warning)
    else:
        logger.info(f"Database {db_name} matches current tidy_tweet version")
