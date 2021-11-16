# flake8: noqa F401
from tidy_tweet.processing import initialise_sqlite, load_twarc_json_to_sqlite
from logging import basicConfig, getLogger
from tidy_tweet.tweet_mapping import create_table_statements as database_schema


basicConfig()


logger = getLogger(__name__)
