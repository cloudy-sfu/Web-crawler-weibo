# Function "search"

`search.py/search`

Searches for a word and a specific time period.  It records all the searching result in SQLite database.

## Parameters

`db`: str

The path of the database, where you have stored the cookies and would store fetched posts.

`table`: str (valid sqlite3 table name)

The table name in the database, where you store fetched posts.

`query`: str

Search query submitted to "weibo"

All posts containing this string will be recorded, 50 pages at most.

`start_time`: tuple[str], datetime (%Y, %m, %d, %H)

[Format code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

The tuple of length 4, where each element is integer. The 4 integers represent year, month, day, hour of the starting time. Posts from this hour will be collected. The time zone is the same as "weibo" server.

`end_time`: tuple[str], datetime (%Y, %m, %d, %H)

The tuple of length 4, where each element is integer. The 4 integers represent year, month, day, hour of the end time. Posts till this hour will be collected. The time zone is the same as "weibo" server.

`max_page`: optional, int

The maximum page to collect. If existed pages are less than this number, the result will be fewer.

## Returns

No returns in Python function.

It creates a database table named `table` (argument) in database `db` (argument), which has the following columns:

`avatar`: str

Link to the avatar of the post author.

`nickname`: str

Username of the post author.

`user_id`: str

User ID of the post author. His/her profile is at https://weibo.com/u/user_id where `user_id` should be replaced with the value from this column.

`posted_time`: str

The time when the post published. Its format can be either "seconds/hours/days ago" or an exact datetime with or without years. It also contains Chinese character which represents "month", "day", "second", "ago", ...

`source`: str

How the post author visit "weibo". It can be either the device name or the topic (tag) name.

`weibo_id`: str

The post can be accessed at https://weibo.com/user_id/weibo_id where `user_id` and `weibo_id` should be replaced with values from the columns.

`content`: str

The text of the post.

`reposts`: str

Number of reposts. If the number exceeds 10 thousands, it will be ended with the Chinese character "万". The character "万" is a unit, which means 10 thousands. (The same will happen in "comments" and "likes".)

`comments`: str

Number of comments.

`likes`: str

Number of likes.