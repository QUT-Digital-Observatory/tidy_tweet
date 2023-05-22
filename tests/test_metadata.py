from tidy_tweet.utilities import get_library_version


def test_get_tidy_tweet_version():
    """Just tests the function runs, can't meaningfully test values"""

    version = get_library_version()

    assert version != "unknown" and version != "unspecified"


# TODO: metadata test
