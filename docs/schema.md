# tidy_tweet database schema

This is an automatically generated document describing the tables and columns in the tidy_tweet database.

```mermaid
erDiagram
    "tweet_url" {
        text tweet_id PK, FK
        text field
        text url PK
        text expanded_url
        text display_url
    }
    "user_url" {
        text user_id PK, FK
        text field
        text url PK
        text expanded_url
        text display_url
    }
    "tweet_hashtag" {
        text tweet_id PK, FK
        text field
        text hashtag PK
        text hashtag_lower
    }
    "user_hashtag" {
        text user_id PK, FK
        text field
        text hashtag PK
        text hashtag_lower
    }
    "tweet_mention" {
        text tweet_id PK, FK
        text field
        text username PK
    }
    "user_mention" {
        text user_id PK, FK
        text field
        text username PK
    }
    "media" {
        text url
        text preview_image_url
        integer height
        integer width
        text type
        integer duration_ms
        integer view_count
        text alt_text
        text media_key PK
    }
    "user_by_page" {
        text name
        text profile_image_url
        text id PK
        text created_at
        text protected
        text description
        text location
        text pinned_tweet_id
        integer verified
        text url
        text username
        integer page_id PK, FK
        text source_file FK
    }
    "tweet_by_page" {
        text id PK
        integer page_id PK, FK
        text reply_settings
        text conversation_id
        text created_at
        text retweeted_tweet_id FK
        text quoted_tweet_id FK
        text replied_to_tweet_id FK
        text in_reply_to_user_id FK
        text author_id FK
        text text
        text lang
        text source
        integer possibly_sensitive
        integer like_count
        integer quote_count
        integer reply_count
        integer retweet_count
        text source_file FK
        integer directly_collected
    }
    "results_page" {
        integer id PK
        text file_name
        text oldest_id
        text newest_id
        integer result_count
        text inserted_at
        text twarc_version
        text tidy_tweet_version
        text retrieved_at
        text request_url
        text additional_metadata
    }
    tweet_url |o--o{ tweet : "tweet"
    user_url |o--o{ user : "user"
    tweet_hashtag |o--o{ tweet : "tweet"
    user_hashtag |o--o{ user : "user"
    tweet_mention |o--o{ tweet : "tweet"
    user_mention |o--o{ user : "user"
    user_by_page |o--o{ results_page : "page"
    user_by_page |o--o{ results_page : "source file"
    tweet_by_page |o--o{ results_page : "page"
    tweet_by_page |o--o{ tweet : "retweeted tweet"
    tweet_by_page |o--o{ tweet : "quoted tweet"
    tweet_by_page |o--o{ tweet : "replied to tweet"
    tweet_by_page |o--o{ user : "in reply to user"
    tweet_by_page |o--o{ user : "author"
    tweet_by_page |o--o{ results_page : "source file"
```

Table **tweet_url**:

- **tweet_id** (text primary key references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the URL is in
- **url** (text primary key not null): t.co shortened URL
- **expanded_url** (text)
- **display_url** (text)

primary key on conflict ignore


Table **user_url**:

- **user_id** (text primary key references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the URL is in
- **url** (text primary key not null): t.co shortened URL
- **expanded_url** (text)
- **display_url** (text)

primary key on conflict ignore


Table **tweet_hashtag**:

- **tweet_id** (text primary key references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the hashtag is in
- **hashtag** (text primary key not null)
- **hashtag_lower** (text): Normalised, as hashtags are case-insensitive on Twitter

primary key on conflict ignore


Table **user_hashtag**:

- **user_id** (text primary key references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the hashtag is in
- **hashtag** (text primary key not null)
- **hashtag_lower** (text): Normalised, as hashtags are case-insensitive on Twitter

primary key on conflict ignore


Table **tweet_mention**:

- **tweet_id** (text primary key references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the mention is in
- **username** (text primary key not null): username of mentioned user

primary key on conflict ignore


Table **user_mention**:

- **user_id** (text primary key references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the mention is in
- **username** (text primary key not null): username of mentioned user

primary key on conflict ignore


Table **media**:

- **url** (text)
- **preview_image_url** (text)
- **height** (integer)
- **width** (integer)
- **type** (text)
- **duration_ms** (integer)
- **view_count** (integer)
- **alt_text** (text)
- **media_key** (text primary key)


Table **user_by_page**:

- **name** (text)
- **profile_image_url** (text)
- **id** (text primary key )
- **created_at** (text)
- **protected** (text)
- **description** (text)
- **location** (text)
- **pinned_tweet_id** (text)
- **verified** (integer): boolean
- **url** (text)
- **username** (text)
- **page_id** (integer primary key references results_page (id))
- **source_file** (text references results_page (file_name))

primary key 


Table **tweet_by_page**:

- **id** (text primary key )
- **page_id** (integer primary key references results_page (id))
- **reply_settings** (text)
- **conversation_id** (text)
- **created_at** (text)
- **retweeted_tweet_id** (text references tweet (id))
- **quoted_tweet_id** (text references tweet (id))
- **replied_to_tweet_id** (text references tweet (id))
- **in_reply_to_user_id** (text references user (id))
- **author_id** (text references user (id))
- **text** (text)
- **lang** (text)
- **source** (text)
- **possibly_sensitive** (integer): boolean
- **like_count** (integer)
- **quote_count** (integer)
- **reply_count** (integer)
- **retweet_count** (integer)
- **source_file** (text references results_page (file_name))
- **directly_collected** (integer): boolean

primary key 


Table **results_page**:

- **id** (integer primary key)
- **file_name** (text)
- **oldest_id** (text): oldest tweet id in page
- **newest_id** (text): newest tweet id in page
- **result_count** (integer): count given in API response
- **inserted_at** (text default current_timestamp)
- **twarc_version** (text)
- **tidy_tweet_version** (text)
- **retrieved_at** (text): time response from twitter was recorded
- **request_url** (text)
- **additional_metadata** (text): extra metadata from twarc and twitter


