import sqlite3
from logging import basicConfig, getLogger
import click
from typing import Union, Collection
from os import PathLike
from pathlib import Path

from tidy_tweet.processing import load_twarc_json_to_sqlite
import tidy_tweet.database as db


basicConfig()


logger = getLogger(__name__)


@click.command()
@click.argument("database", type=click.Path(path_type=Path), required=True)
@click.argument("json_files", type=click.Path(exists=True), nargs=-1)
def tidy_twarc_jsons(database: Path, json_files: Collection[Union[str, PathLike]]):
    """
    Tidies Twitter json collected with Twarc into relational tables.

    Can take one or more JSON_FILES (produced by Twarc) as input, tidies the
    tweet data within those files, and stores the date in DATABASE.

    DATABASE is the filename for the tidy data database (should end in .db), for
    example: my_dataset.db . This will be created as an SQLite database file.

    Files can be added to an existing DATABASE file, if the same version of tidy_tweet
    is used for all insertions into the one DATABASE.

    Note that at this time tidy_tweet only works with Twitter data from the Twitter
    v2 API, as collected with twarc2.

    Full documentation: https://github.com/QUT-Digital-Observatory/tidy_tweet

    """
    # Check database
    if database.exists():
        # If database does exist, check the schema version
        try:
            db.check_database_version(database)
        except db.SchemaVersionMismatchError as e:
            raise click.UsageError(e.message()) from e
        except sqlite3.DatabaseError as e:
            raise click.BadParameter(
                f"{database} is not a database file.", param_hint="database"
            ) from e
        except Exception as e:
            raise e

        click.echo("Using existing tidy tweet database: " + str(database))
    else:
        # If database doesn't exist, initialise it
        click.echo("Creating new tidy tweet database: " + str(database))
        db.initialise_sqlite(database)

    # Load files into database
    num_files = len(json_files)
    n = 0
    total_pages = 0
    for file in json_files:
        n = n + 1  # Count files for user messaging only
        click.echo(f"Loading {file} (file {n} of {num_files}) into {database}")
        p = load_twarc_json_to_sqlite(file, database)
        total_pages = total_pages + p
        click.echo(f"{p} pages of Twitter results loaded from {file}")

    click.echo(
        f"All done! {total_pages} pages of tweets loaded into {database} from {n} "
        f"files."
    )


if __name__ == "__main__":
    tidy_twarc_jsons()
