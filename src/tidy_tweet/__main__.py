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
@click.argument("db_name", type=click.Path(), path_type=Path)
@click.argument("json_files", type=click.Path(exists=True), nargs=-1)
def tidy_twarc_jsons(
        db_name: Path,
        json_files: Collection[Union[str, PathLike]]
):
    # Check database
    if db_name.exists():
        # If database does exist, check the schema version
        try:
            db.check_database_version(db_name)
        except db.SchemaVersionMismatchError as e:
            click.echo(e.message())
            raise click.Abort from e
        click.echo("Using existing tidy tweet database: " + str(db_name))
    else:
        # If database doesn't exist, initialise it
        click.echo("Creating new tidy tweet database: " + str(db_name))
        db.initialise_sqlite(db_name)

    # Load files into database
    num_files = len(json_files)
    n = 0
    total_pages = 0
    for file in json_files:
        n = n + 1  # Count files for user messaging only
        click.echo(f"Loading {file} (file {n} of {num_files}) into {db_name}")
        p = load_twarc_json_to_sqlite(file, db_name)
        total_pages = total_pages + p
        click.echo(f"{p} pages of Twitter results loaded from {file}")

    click.echo(f"All done! {total_pages} pages of tweets loaded into {db_name} from {n} files.")


if __name__ == '__main__':
    tidy_twarc_jsons()
