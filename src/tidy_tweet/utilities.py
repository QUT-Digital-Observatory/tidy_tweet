from typing import Dict, Any, List
from logging import getLogger

logger = getLogger(__name__)


def add_mappings(to_extend: Dict[Any, List], addition: Dict[Any, List]):
    """
    Appends all the mappings for each table from `addition` into `to_extend`.
    """
    for table in addition.keys():
        if table not in to_extend:
            to_extend[table] = []

        to_extend[table].extend(addition[table])


def clean_sql_statement(original: str) -> str:
    """
    Cleans up SQL statements so that they end with a semicolon and don't have any
    leading or trailing whitespace
    """
    clean = original.strip()
    if not clean.endswith(";"):
        clean = clean + ";"
    return clean


def get_library_version() -> str:
    version = "unknown"

    try:
        from tidy_tweet._version import version
    except ImportError:
        version = "unspecified"
        logger.warn(
            "WARNING: cannot store tidy_tweet version in database as version could not "
            "be fetched. If running tidy_tweet from source, try installing package in "
            "editable mode."
        )

    return version
