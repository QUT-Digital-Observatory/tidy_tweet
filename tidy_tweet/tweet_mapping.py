from typing import Dict, List


sql_by_table: Dict[str, Dict[str, str]] = {}


# --- Includes tables ---

# media
sql_by_table['media'] = {
    'create': """
create table media (
    url text,
    height integer,
    width integer,
    type text,
    media_key text primary key
)
    """,
    'insert': """
insert or ignore into media (
    media_key, url, type,
    height, width
) values (
    :media_key, :url, :type,
    :height, :width
)
    """
}


def map_media(media_list_json) -> Dict[str, List[Dict]]:
    mapped_media = []
    for media_json in media_list_json:
        mapped_media.append({
            "media_key": media_json["media_key"],
            "url": media_json["url"],
            "type": media_json["type"],
            "height": media_json["height"],
            "width": media_json["width"]
        })
    return {'media': mapped_media}


# places - TODO

# users
# TODO: Fields not included yet:
# - public_metrics
# - entities
sql_by_table['media'] = {
    'create': """
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
    'insert': """
insert into user (
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
    """
}


def map_user(user_json) -> Dict[str, List[Dict]]:
    user_map = {
        'id': user_json['id'],
        'username': user_json['username'],
        'name': user_json['name'],
        'url': user_json['url'],
        'profile_image_url': user_json['profile_image_url'],
        'description': user_json['description'],
        'created_at': user_json['created_at'],
        'protected': user_json['protected'],
        'verified': user_json['verified'],
        'location': user_json['location'],
        'pinned_tweet_id': user_json['pinned_tweet_id']
    }
    return {'user': [user_map]}

# todo: tweets - any differences from top level tweet object?


# --- tweet tables ---
# TODO: fields not yet included:
# - referenced_tweets not properly implemented
# - entities
# - context_annotations
# - public_metrics

sql_by_table["tweet"] = {
    'create': """
create table tweet (
    reply_settings text,
    conversation_id text,
    created_at text,
    retweeted_tweet_id text,
    author_id text references user (id),
    id text primary key,
    text text,
    lang text,
    source text,
    possibly_sensitive integer -- boolean
)
    """,
    'insert': """
insert or ignore into tweet (
    id, author_id,
    text, lang, source,
    possibly_sensitive, reply_settings,
    created_at,
    conversation_id,
    retweeted_tweet_id,
    quoted_tweet_id
) values (
    :id, :author_id,
    :text, :lang, :source,
    :possibly_sensitive, :reply_settings,
    :created_at,
    :conversation_id,
    :retweeted_tweet_id
)
    """
}


def map_tweet(tweet_json) -> Dict[str, List[Dict]]:
    tweet_map = {
        "id": tweet_json["id"],
        "author_id": tweet_json["author_id"],
        "text": tweet_json["text"],
        "lang": tweet_json["lang"],
        "source": tweet_json["source"],
        "possibly_sensitive": tweet_json["possibly_sensitive"],
        "reply_settings": tweet_json["reply_settings"],
        "created_at": tweet_json["created_at"],
        "conversation_id": tweet_json["conversation_id"]
    }
    
    # TODO: handle all referenced tweets & entities, as objects/relationships as appropriate
    rt_id = None
    if 'referenced_tweets' in tweet_json and len(tweet_json['referenced_tweets']) > 0:
        for t in tweet_json['referenced_tweets']:
            if t['type'] == 'retweeted':
                rt_id = t['id']
                break
    tweet_map["retweeted_tweet_id"] = rt_id

    return {'tweet': [tweet_map]}



# --- Validation ---

# We have both create and assert statements for all tables
for table_sql in sql_by_table.values():
    assert {'create', 'insert'} <= table_sql.keys()


# --- Convenience lists ---
def clean_sql_statement(original: str) -> str:
    """
    Cleans up SQL statements so they end with a semicolon and don't have any leading or
    trailing whitespace
    """
    clean = original.strip()
    if not clean.endswith(';'):
        clean = clean + ';'
    return clean


create_table_statements = [clean_sql_statement(tbl['create']) for tbl in sql_by_table.values()]
