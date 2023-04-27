# tidy_tweet database schema

This is an automatically generated document describing the tables and columns in the tidy_tweet database.

```mermaid
erDiagram
    "tweet_url" {
        text tweet_id FK
        text field
        text url
        text expanded_url
        text display_url
    }
    "user_url" {
        text user_id FK
        text field
        text url
        text expanded_url
        text display_url
    }
    "tweet_hashtag" {
        text tweet_id FK
        text field
        text tag
    }
    "user_hashtag" {
        text user_id FK
        text field
        text tag
    }
    "tweet_mention" {
        text tweet_id FK
        text field
        text username
    }
    "user_mention" {
        text user_id FK
        text field
        text username
    }
    "media" {
        text url
        text preview_image_url
        integer height
        integer width
        text type
        integer duration_ms
        integer view_count
        string alt_text
        text media_key PK
    }
    "user" {
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
    }
    "tweet" {
        text id PK
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
        integer directly_collected
    }
    "_metadata" {
        text metadata_key
        text metadata_value
    }
    tweet_url |o--o{ tweet : "tweet"
    user_url |o--o{ user : "user"
    tweet_hashtag |o--o{ tweet : "tweet"
    user_hashtag |o--o{ user : "user"
    tweet_mention |o--o{ tweet : "tweet"
    user_mention |o--o{ user : "user"
    tweet |o--o{ tweet : "retweeted tweet"
    tweet |o--o{ tweet : "quoted tweet"
    tweet |o--o{ tweet : "replied to tweet"
    tweet |o--o{ user : "in reply to user"
    tweet |o--o{ user : "author"
```

Table **tweet_url**:
- **tweet_id** (text references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the URL is in
- **url** (text not null): t.co shortened URL
- **expanded_url** (text)
- **display_url** (text)

Table **user_url**:
- **user_id** (text references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the URL is in
- **url** (text not null): t.co shortened URL
- **expanded_url** (text)
- **display_url** (text)

Table **tweet_hashtag**:
- **tweet_id** (text references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the hashtag is in
- **tag** (text not null)

Table **user_hashtag**:
- **user_id** (text references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the hashtag is in
- **tag** (text not null)

Table **tweet_mention**:
- **tweet_id** (text references tweet (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the mention is in
- **username** (text not null): username of mentioned user

Table **user_mention**:
- **user_id** (text references user (id))
- **field** (text not null): e.g. "description", "text" - which field of the source object the mention is in
- **username** (text not null): username of mentioned user

Table **media**:
- **url** (text)
- **preview_image_url** (text)
- **height** (integer)
- **width** (integer)
- **type** (text)
- **duration_ms** (integer)
- **view_count** (integer)
- **alt_text** (string)
- **media_key** (text primary key)

Table **user**:
- **name** (text)
- **profile_image_url** (text)
- **id** (text primary key)
- **created_at** (text)
- **protected** (text)
- **description** (text)
- **location** (text)
- **pinned_tweet_id** (text)
- **verified** (integer): boolean
- **url** (text)
- **username** (text)

Table **tweet**:
- **id** (text primary key)
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
- **directly_collected** (integer): boolean

Table **_metadata**:
- **metadata_key** (text): primary key on conflict fail,
- **metadata_value** (text)

