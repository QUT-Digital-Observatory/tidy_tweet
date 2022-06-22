from click.testing import CliRunner
from tidy_tweet.__main__ import tidy_twarc_jsons


def test_no_args():
    runner = CliRunner()

    # No arguments - should fail
    result = runner.invoke(tidy_twarc_jsons, [])
    assert result.exit_code != 0


def test_one_arg(tmp_path):
    db_path = tmp_path / "one.db"

    runner = CliRunner()

    # Just a non-existing database - should create an empty db
    result = runner.invoke(tidy_twarc_jsons, [str(db_path)])
    assert result.exit_code == 0
    assert db_path.exists()

    # Just an empty existing database - should not fail on validation because
    # the database schema and structure are valid, just empty.
    result = runner.invoke(tidy_twarc_jsons, [str(db_path)])
    assert result.exit_code == 0

    # Just a json file - should fail
