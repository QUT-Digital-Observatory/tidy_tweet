from tidy_tweet.tweet_mapping import map_tidy_tweet_metadata


def test_get_tidy_tweet_version():
    """Just tests the function runs, can't meaningfully test values"""

    code_versions = map_tidy_tweet_metadata()

    assert len(code_versions["_metadata"]) == 2
