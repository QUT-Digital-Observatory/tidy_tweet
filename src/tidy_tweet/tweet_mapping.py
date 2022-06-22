from typing import Dict, List
from tidy_tweet.utilities import add_mappings
from logging import getLogger


logger = getLogger(__name__)


# --- SCHEMA VERSION ---
# Update this every time the database schema is changed!
SCHEMA_VERSION = "2022-03-10"


sql_by_table: Dict[str, Dict[str, str]] = {}


# --- Entities tables ---
# URLs
sql_by_table["url"] = {
    "create": """
create table url (
    source_id text, -- the id of the object (user or tweet) this URL is included in
    source_type text, -- "user" or "tweet"
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the URL is in
    url text not null, -- t.co shortened URL
    expanded_url text,
    display_url text
)
    """,
    "insert": """
insert into url (
    source_id, source_type, field,
    url, expanded_url, display_url
) values (
    :source_id, :source_type, :field,
    :url, :expanded_url, :display_url
)
    """,
}


def map_urls(
    source_id: str, source_type: str, field: str, url_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    url_maps = []

    for url_json in url_json_list:
        url_maps.append(
            {
                "source_id": source_id,
                "source_type": source_type,
                "field": field,
                "url": url_json["url"],
                # These fields are not guaranteed to be present - if a user
                # copies and pastes a shortened url into a profile, it won't
                # be expanded - eg https://twitter.com/SAHU_Finance
                "expanded_url": url_json.get("expanded_url", None),
                "display_url": url_json.get("display_url", None),
            }
        )

    return {"url": url_maps}


# Hashtags
sql_by_table["hashtag"] = {
    "create": """
create table hashtag (
    source_id text, -- the id of the object (user or tweet) this hashtag is included in
    source_type text, -- "user" or "tweet"
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the hashtag is in
    tag text not null
)
    """,
    "insert": """
insert into hashtag (
    source_id, source_type, field,
    tag
) values (
    :source_id, :source_type, :field,
    :tag
)
    """,
}


def map_hashtags(
    source_id: str, source_type: str, field: str, tag_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    tag_mappings = [
        {
            "source_id": source_id,
            "source_type": source_type,
            "field": field,
            "tag": t["tag"],
        }
        for t in tag_json_list
    ]
    return {"hashtag": tag_mappings}


# Mentions
sql_by_table["mention"] = {
    "create": """
create table mention (
    source_id text, -- the id of the object (user or tweet) this mention is included in
    source_type text, -- "user" or "tweet"
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the mention is in
    username text not null -- username of mentioned user
)
    """,
    "insert": """
insert into mention (
    source_id, source_type, field,
    username
) values (
    :source_id, :source_type, :field,
    :username
)
    """,
}


def map_mentions(
    source_id: str, source_type: str, field: str, mention_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    mention_mappings = [
        {
            "source_id": source_id,
            "source_type": source_type,
            "field": field,
            "username": t["username"],
        }
        for t in mention_json_list
    ]
    return {"mention": mention_mappings}


# Entities objects
def map_entities(source_id, source_type, field, entities_json) -> Dict[str, List[Dict]]:
    mappings = {}

    for entity_type, entity_data in entities_json.items():
        if entity_type == "urls":
            add_mappings(mappings, map_urls(source_id, source_type, field, entity_data))
        if entity_type == "hashtags":
            add_mappings(
                mappings, map_hashtags(source_id, source_type, field, entity_data)
            )
        if entity_type == "mentions":
            add_mappings(
                mappings, map_mentions(source_id, source_type, field, entity_data)
            )

    return mappings


# --- Includes tables ---

# media
sql_by_table["media"] = {
    "create": """
create table media (
    url text,
    preview_image_url text,
    height integer,
    width integer,
    type text,
    duration_ms integer,
    view_count integer,
    alt_text string,
    media_key text primary key
)
    """,
    "insert": """
insert or ignore into media (
    media_key, url, type,
    height, width, preview_image_url, alt_text,
    duration_ms, view_count
) values (
    :media_key, :url, :type,
    :height, :width, :preview_image_url, :alt_text,
    :duration_ms, :view_count
)
    """,
}


def map_media(media_list_json) -> Dict[str, List[Dict]]:
    mapped_media = []
    for media_json in media_list_json:
        try:
            view_count = media_json["public_metrics"]["view_count"]
        except KeyError:
            view_count = None

        mapped_media.append(
            {
                "media_key": media_json["media_key"],
                "url": media_json.get("url", None),
                "type": media_json.get("type", None),
                "height": media_json.get("height", None),
                "width": media_json.get("width", None),
                "preview_image_url": media_json.get("preview_image_url", None),
                "alt_text": media_json.get("alt_text", None),
                "duration_ms": media_json.get("duration_ms", None),
                "view_count": view_count,
            }
        )
    return {"media": mapped_media}


# places - TODO

# users
# TODO: Fields not included yet:
# - public_metrics
sql_by_table["user"] = {
    "create": """
create table user (
    name text,
    profile_image_url text,
    id text primary key,
    created_at text,
    protected text,
    description text,
    location text,
    pinned_tweet_id text,
    verified integer, -- boolean
    url text,
    username text
)
    """,
    "insert": """
insert or ignore into user (
    id, username, name, url,
    profile_image_url, description,
    created_at,
    protected, verified,
    location,
    pinned_tweet_id
) values (
    :id, :username, :name, :url,
    :profile_image_url, :description,
    :created_at,
    :protected, :verified,
    :location,
    :pinned_tweet_id
)
    """,
}


def map_user(user_json) -> Dict[str, List[Dict]]:
    user_map = {
        "id": user_json["id"],
        "username": user_json["username"],
        "name": user_json["name"],
        "url": user_json["url"],
        "profile_image_url": user_json["profile_image_url"],
        "description": user_json.get("description", None),
        "created_at": user_json["created_at"],
        "protected": user_json["protected"],
        "verified": user_json["verified"],
        "location": user_json.get("location", None),
        "pinned_tweet_id": user_json.get("pinned_tweet_id", None),
    }

    mappings = {"user": [user_map]}

    # Entities
    if "entities" in user_json:
        for field, entities in user_json["entities"].items():
            add_mappings(
                mappings, map_entities(user_json["id"], "user", field, entities)
            )

    return mappings


# --- tweet tables ---
# TODO: fields not yet included:
# - entities
# - context_annotations

sql_by_table["tweet"] = {
    "create": """
create table tweet (
    id text primary key,
    reply_settings text,
    conversation_id text,
    created_at text,
    retweeted_tweet_id text references tweet (id),
    quoted_tweet_id text references tweet (id),
    replied_to_tweet_id text references tweet (id),
    in_reply_to_user_id text references user (id),
    author_id text references user (id),
    text text,
    lang text,
    source text,
    possibly_sensitive integer, -- boolean
    like_count integer,
    quote_count integer,
    reply_count integer,
    retweet_count integer,
    directly_collected integer -- boolean
)
    """,
    "insert": """
insert or ignore into tweet (
    id, author_id,
    text, lang, source,
    possibly_sensitive, reply_settings,
    created_at,
    conversation_id,
    retweeted_tweet_id,
    quoted_tweet_id,
    replied_to_tweet_id,
    in_reply_to_user_id,
    like_count, quote_count, reply_count, retweet_count,
    directly_collected
) values (
    :id, :author_id,
    :text, :lang, :source,
    :possibly_sensitive, :reply_settings,
    :created_at,
    :conversation_id,
    :retweeted_tweet_id,
    :quoted_tweet_id,
    :replied_to_tweet_id,
    :in_reply_to_user_id,
    :like_count, :quote_count, :reply_count, :retweet_count,
    :directly_collected
)
    """,
}


def map_tweet(tweet_json, directly_collected: bool) -> Dict[str, List[Dict]]:
    tweet_map = {
        "id": tweet_json["id"],
        "author_id": tweet_json["author_id"],
        "text": tweet_json["text"],
        "lang": tweet_json["lang"],
        "source": tweet_json.get("source", None),
        "possibly_sensitive": tweet_json["possibly_sensitive"],
        "reply_settings": tweet_json["reply_settings"],
        "created_at": tweet_json["created_at"],
        "conversation_id": tweet_json["conversation_id"],
        "in_reply_to_user_id": None,
        "like_count": tweet_json["public_metrics"]["like_count"],
        "quote_count": tweet_json["public_metrics"]["quote_count"],
        "reply_count": tweet_json["public_metrics"]["reply_count"],
        "retweet_count": tweet_json["public_metrics"]["retweet_count"],
        "directly_collected": directly_collected,
    }

    if "in_reply_to_user_id" in tweet_json:
        tweet_map["in_reply_to_user_id"] = tweet_json["in_reply_to_user_id"]

    # A tweet can have no more than one referenced tweet per type, but may have
    # multiple references of different types.
    # e.g. a tweet may have both a quoted tweet and a replied to tweet, but can't
    # have two replied_to tweets.
    rt_id = None
    qt_id = None
    replied_to_id = None
    if "referenced_tweets" in tweet_json and len(tweet_json["referenced_tweets"]) > 0:
        for t in tweet_json["referenced_tweets"]:
            if t["type"] == "retweeted":
                rt_id = t["id"]
            elif t["type"] == "quoted":
                qt_id = t["id"]
            elif t["type"] == "replied_to":
                replied_to_id = t["id"]
    tweet_map["retweeted_tweet_id"] = rt_id
    tweet_map["quoted_tweet_id"] = qt_id
    tweet_map["replied_to_tweet_id"] = replied_to_id

    mappings = {"tweet": [tweet_map]}

    # Entities
    if "entities" in tweet_json:
        add_mappings(
            mappings,
            map_entities(tweet_json["id"], "tweet", "text", tweet_json["entities"]),
        )

    return mappings


# --- Metadata ---

sql_by_table["_metadata"] = {
    "create": """
create table _metadata (
    metadata_key text, --primary key on conflict fail,
    metadata_value text
)
    """,
    "insert": """
insert into _metadata (metadata_key, metadata_value)
    values (:metadata_key, :metadata_value)
    """,
}


def map_twarc_metadata(twarc_metadata_json) -> Dict[str, List[Dict]]:
    # Rename the "version" key for clarity
    twarc_metadata_json["twarc_version"] = twarc_metadata_json.pop("version")
    return {
        "_metadata": [
            {"metadata_key": k, "metadata_value": v}
            for k, v in twarc_metadata_json.items()
        ]
    }


def map_tidy_tweet_metadata() -> Dict[str, List[Dict]]:
    try:
        from tidy_tweet._version import version
    except ImportError:
        version = "unspecified"
        logger.warn(
            "WARNING: cannot store tidy_tweet version in database as version could not "
            "be fetched. If running tidy_tweet from source, try installing package in "
            "editable mode."
        )

    # TODO: how to handle db with additions of files with different library versions?
    return {
        "_metadata": [
            {"metadata_key": "schema_version", "metadata_value": SCHEMA_VERSION},
            {"metadata_key": "tidy_tweet_version", "metadata_value": version},
        ]
    }


# --- Validation ---

# We have both create and assert statements for all tables
for table_sql in sql_by_table.values():
    assert {"create", "insert"} <= table_sql.keys()


# --- Convenience lists ---
def clean_sql_statement(original: str) -> str:
    """
    Cleans up SQL statements so that they end with a semicolon and don't have any
    leading or trailing whitespace
    """
    clean = original.strip()
    if not clean.endswith(";"):
        clean = clean + ";"
    return clean


create_table_statements = [
    clean_sql_statement(tbl["create"]) for tbl in sql_by_table.values()
]
