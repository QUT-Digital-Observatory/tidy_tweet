from typing import Dict, List
from tidy_tweet.utilities import add_mappings, clean_sql_statement
from json import dumps
from logging import getLogger

logger = getLogger(__name__)


try:
    from tidy_tweet._version import version
except ImportError:
    version = "unspecified"
    logger.warn(
        "WARNING: cannot store tidy_tweet version in database as version could not "
        "be fetched. If running tidy_tweet from source, try installing package in "
        "editable mode."
    )


# --- SCHEMA VERSION ---
# Update this every time the database schema is changed!
SCHEMA_VERSION = "2023-06-22"


sql_by_table: Dict[str, Dict[str, str]] = {}
sql_views: Dict[str, str] = {}

# --- Entities tables ---
# URLs
# URLs from tweets
sql_by_table["tweet_url"] = {
    "create": """
create table tweet_url (
    tweet_id text references tweet (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the URL is in
    url text not null, -- t.co shortened URL
    expanded_url text,
    display_url text,
    primary key (tweet_id, url) on conflict ignore
)
    """,
    "insert": """
insert into tweet_url (
    tweet_id, field,
    url, expanded_url, display_url
) values (
    :source_id, :field,
    :url, :expanded_url, :display_url
)
    """,
}
# URLs from user profiles
sql_by_table["user_url"] = {
    "create": """
create table user_url (
    user_id text references user (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the URL is in
    url text not null, -- t.co shortened URL
    expanded_url text,
    display_url text,
    primary key (user_id, url) on conflict ignore
)
    """,
    "insert": """
insert into user_url (
    user_id, field,
    url, expanded_url, display_url
) values (
    :source_id, :field,
    :url, :expanded_url, :display_url
)
    """,
}


def map_urls(
    source_id: str, source_type: str, field: str, url_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    table_name = "tweet_url" if source_type == "tweet" else "user_url"

    url_maps = []
    for url_json in url_json_list:
        url_maps.append(
            {
                "source_id": source_id,
                "field": field,
                "url": url_json["url"],
                # These fields are not guaranteed to be present - if a user
                # copies and pastes a shortened url into a profile, it won't
                # be expanded - eg https://twitter.com/SAHU_Finance
                "expanded_url": url_json.get("expanded_url", None),
                "display_url": url_json.get("display_url", None),
            }
        )

    return {table_name: url_maps}


# Hashtags
# Hashtags from tweets
sql_by_table["tweet_hashtag"] = {
    "create": """
create table tweet_hashtag (
    tweet_id text references tweet (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the hashtag is in
    hashtag text not null,
    hashtag_lower text, -- Normalised, as hashtags are case-insensitive on Twitter
    primary key (tweet_id, hashtag) on conflict ignore
)
    """,
    "insert": """
insert into tweet_hashtag (
    tweet_id, field,
    hashtag, hashtag_lower
) values (
    :source_id, :field,
    :hashtag, :hashtag_lower
)
    """,
}
# Hashtags from user profiles
sql_by_table["user_hashtag"] = {
    "create": """
create table user_hashtag (
    user_id text references user (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the hashtag is in
    hashtag text not null,
    hashtag_lower text, -- Normalised, as hashtags are case-insensitive on Twitter
    primary key (user_id, hashtag) on conflict ignore
)
    """,
    "insert": """
insert into user_hashtag (
    user_id, field,
    hashtag, hashtag_lower
) values (
    :source_id, :field,
    :hashtag, :hashtag_lower
)
    """,
}


def map_hashtags(
    source_id: str, source_type: str, field: str, tag_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    table_name = "tweet_hashtag" if source_type == "tweet" else "user_hashtag"

    tag_mappings = [
        {
            "source_id": source_id,
            "field": field,
            "hashtag": t["tag"],
            # Note that lower() could be done in SQLite by making hashtag_lower a
            # generated column, however the SQLite lower() only handles ASCII while
            # the python str.lower() handles Unicode
            "hashtag_lower": t["tag"].lower(),
        }
        for t in tag_json_list
    ]
    return {table_name: tag_mappings}


# Mentions
# Mentions in tweets
sql_by_table["tweet_mention"] = {
    "create": """
create table tweet_mention (
    tweet_id text references tweet (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the mention is in
    username text not null, -- username of mentioned user
    primary key (tweet_id, username) on conflict ignore
)
    """,
    "insert": """
insert into tweet_mention (
    tweet_id, field,
    username
) values (
    :source_id, :field,
    :username
)
    """,
}
# Mentions in user profiles
sql_by_table["user_mention"] = {
    "create": """
create table user_mention (
    user_id text references user (id),
    field text not null, -- e.g. "description", "text" - which field of the source
                         -- object the mention is in
    username text not null, -- username of mentioned user
    primary key (user_id, username) on conflict ignore
)
    """,
    "insert": """
insert into user_mention (
    user_id, field,
    username
) values (
    :source_id, :field,
    :username
)
    """,
}


def map_mentions(
    source_id: str, source_type: str, field: str, mention_json_list: List[Dict]
) -> Dict[str, List[Dict]]:
    table_name = "tweet_mention" if source_type == "tweet" else "user_mention"

    mention_mappings = [
        {
            "source_id": source_id,
            "field": field,
            "username": t["username"],
        }
        for t in mention_json_list
    ]
    return {table_name: mention_mappings}


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
    alt_text text,
    media_key text primary key
)
    """,
    "insert": """
insert or replace into media (
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
sql_by_table["user_by_page"] = {
    "create": """
create table user_by_page (
    name text,
    profile_image_url text,
    id text,
    created_at text,
    protected text,
    description text,
    location text,
    pinned_tweet_id text,
    verified integer, -- boolean
    url text,
    username text,
    source_page integer references results_page (page),
    source_file text references results_page (file_name),
    primary key (id, source_file, source_page)
)
    """,
    "insert": """
insert or ignore into user_by_page (
    id, username, name, url,
    profile_image_url, description,
    created_at,
    protected, verified,
    location,
    pinned_tweet_id,
    source_page, source_file
) values (
    :id, :username, :name, :url,
    :profile_image_url, :description,
    :created_at,
    :protected, :verified,
    :location,
    :pinned_tweet_id,
    :page_num, :source_file
)
    """,
}
sql_views[
    "user"
] = """
create view user as
select
    user_by_page.id, username, name, url,
    profile_image_url, description,
    created_at,
    protected, verified,
    location,
    pinned_tweet_id,
    max(retrieved_at) as retrieved_at
from user_by_page
left join results_page on
    user_by_page.source_page = results_page.page
    and user_by_page.source_file = results_page.file_name
group by user_by_page.id
"""


def map_user(user_json, source_file, page_num) -> Dict[str, List[Dict]]:
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
        "source_file": source_file,
        "page_num": page_num,
    }

    mappings = {"user_by_page": [user_map]}

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

sql_by_table["tweet_by_page"] = {
    "create": """
create table tweet_by_page (
    id text,
    source_page integer references results_page (page),
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
    source_file text references results_page (file_name),
    directly_collected integer, -- boolean
    primary key (id, source_file, source_page)
)
    """,
    "insert": """
insert or ignore into tweet_by_page (
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
    directly_collected, source_file, source_page
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
    :directly_collected, :source_file, :source_page
)
    """,
}
sql_views[
    "tweet"
] = """
create view tweet as
select
    tweet_by_page.id, author_id,
    text, lang, source,
    possibly_sensitive, reply_settings,
    created_at,
    conversation_id,
    retweeted_tweet_id,
    quoted_tweet_id,
    replied_to_tweet_id,
    in_reply_to_user_id,
    like_count, quote_count, reply_count, retweet_count,
    max(retrieved_at) as retrieved_at
from tweet_by_page
left join results_page on
    tweet_by_page.source_page = results_page.page
    and tweet_by_page.source_file = results_page.file_name
group by tweet_by_page.id
"""


def map_tweet(
    tweet_json, directly_collected: bool, source_file: str, page_num
) -> Dict[str, List[Dict]]:
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
        "source_file": source_file,
        "source_page": page_num,
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

    mappings = {"tweet_by_page": [tweet_map]}

    # Entities
    if "entities" in tweet_json:
        add_mappings(
            mappings,
            map_entities(tweet_json["id"], "tweet", "text", tweet_json["entities"]),
        )

    return mappings


# --- Metadata ---
# --- Results files
sql_by_table["results_page"] = {
    "create": """
create table results_page (
    page integer,  -- page number within the file
    file_name text,
    oldest_id text,  -- oldest tweet id in page
    newest_id text,  -- newest tweet id in page
    result_count integer,  -- count given in API response
    inserted_at text default current_timestamp,
    twarc_version text,
    tidy_tweet_version text,
    retrieved_at text, -- time response from twitter was recorded
    request_url text,
    additional_metadata text, -- extra metadata from twarc and twitter
    primary key (file_name, page)
)
    """,
    "insert": """
insert into results_page (
    page, file_name,
    oldest_id, newest_id, result_count,
    retrieved_at, request_url,
    twarc_version, tidy_tweet_version,
    additional_metadata
) values (
    :page, :file_name,
    :oldest_id, :newest_id, :result_count,
    :retrieved_at, :request_url,
    :twarc_version, :tidy_tweet_version,
    :additional_metadata
)
    """,
}
sql_views[
    "results_file"
] = """
create view results_file as
select
    file_name,
    min(oldest_id) as oldest_id,  -- oldest tweet id in file
    max(newest_id) as newest_id,  -- newest tweet id in file
    sum(result_count) as result_count,  -- count given in API response
    -- (sum of all page result counts)
    max(inserted_at) as inserted_at,
    twarc_version,
    min(retrieved_at) as retrieved_at_min, -- earliest retrieval time for pages in file
    max(retrieved_at) as retrieved_at_max -- latest retrieval time for pages in file
from results_page
group by file_name
"""


def map_page_metadata(
    filename: str, page_num: int, page_metadata_json: Dict, twarc_metadata_json: Dict
) -> Dict:
    metadata = {"file_name": filename, "page": page_num}

    # Tidy tweet metadata
    metadata["tidy_tweet_version"] = version

    # Twitter result page metadata
    key_columns = ["oldest_id", "newest_id", "result_count"]
    for key in key_columns:
        metadata[key] = page_metadata_json.pop(key, None)

    # Twarc metadatas
    metadata["twarc_version"] = twarc_metadata_json.pop("version", None)
    metadata["request_url"] = twarc_metadata_json.pop("url", None)
    metadata["retrieved_at"] = twarc_metadata_json.pop("retrieved_at")

    # Any unexpected items in either metadata should be retained
    extras = {}

    if len(page_metadata_json) > 0:
        extras["twarc"] = page_metadata_json

    if len(twarc_metadata_json) > 0:
        extras["twarc"] = twarc_metadata_json

    metadata["additional_metadata"] = dumps(extras, ensure_ascii=False)

    return metadata


# --- Validation ---

# We have both create and assert statements for all tables
for table_sql in sql_by_table.values():
    assert {"create", "insert"} <= table_sql.keys()


# --- Convenience lists ---


def get_create_table_statements(strict_mode=True):
    strict = " strict" if strict_mode else ""
    return [
        clean_sql_statement(tbl["create"] + strict) for tbl in sql_by_table.values()
    ]
