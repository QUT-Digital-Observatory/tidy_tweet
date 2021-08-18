# tidy_tweet

This is *extremely preliminary*. Not all entities/fields are loaded. Library structure
will change.

## To use

```python
from tidy_tweet import initialise_sqlite, load_twarc_json_to_sqlite

initialise_sqlite('database_name')
load_twarc_json_to_sqlite('twarc2_output_json', 'database_name')
```