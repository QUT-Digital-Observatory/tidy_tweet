from tidy_tweet import initialise_sqlite, load_twarc_json_to_sqlite
from pathlib import Path
import sqlite3


data_directory = Path(__file__).parent.resolve() / "data"

timeline_json_file = data_directory / "ObservatoryTeam.jsonl"


def test_load_timeline(tmp_path):
    """
    Checks that a timeline search file (produced by `twarc2 timeline ObservatoryTeam`)
    can be parsed without errors. Performs some basic checks that the resulting data is
    as expected.
    """
    db_path = tmp_path / "ObservatoryTeam.db"

    initialise_sqlite(db_path)

    load_twarc_json_to_sqlite(timeline_json_file, db_path)

    with sqlite3.connect(db_path) as conn:
        db = conn.cursor()

        # Check number of tweets
        db.execute(
            """
            select directly_collected, count(*)
            from tweet
            group by directly_collected;
         """
        )

        for directly_collected, num_tweets in db:
            if directly_collected == 0:
                assert num_tweets == 177
            else:
                assert num_tweets == 204
