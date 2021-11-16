from typing import Dict, List
from tidy_tweet.utilities import add_mappings


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
    expanded_url text not null,
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
                "expanded_url": url_json["expanded_url"],
                "display_url": url_json["display_url"],
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
    height integer,
    width integer,
    type text,
    media_key text primary key
)
    """,
    "insert": """
insert or ignore into media (
    media_key, url, type,
    height, width
) values (
    :media_key, :url, :type,
    :height, :width
)
    """,
}


def map_media(media_list_json) -> Dict[str, List[Dict]]:
    mapped_media = []
    for media_json in media_list_json:
        mapped_media.append(
            {
                "media_key": media_json["media_key"],
                "url": media_json["url"],
                "type": media_json["type"],
                "height": media_json["height"],
                "width": media_json["width"],
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
        "description": user_json["description"] if "description" in user_json else None,
        "created_at": user_json["created_at"],
        "protected": user_json["protected"],
        "verified": user_json["verified"],
        "location": user_json["location"] if "location" in user_json else None,
        "pinned_tweet_id": user_json["pinned_tweet_id"]
        if "pinned_tweet_id" in user_json
        else None,
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
        "source": tweet_json["source"],
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
    # have two replied to tweets.
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


# --- Validation ---

# We have both create and assert statements for all tables
for table_sql in sql_by_table.values():
    assert {"create", "insert"} <= table_sql.keys()


# --- Convenience lists ---
def clean_sql_statement(original: str) -> str:
    """
    Cleans up SQL statements so they end with a semicolon and don't have any leading or
    trailing whitespace
    """
    clean = original.strip()
    if not clean.endswith(";"):
        clean = clean + ";"
    return clean


create_table_statements = [
    clean_sql_statement(tbl["create"]) for tbl in sql_by_table.values()
]
