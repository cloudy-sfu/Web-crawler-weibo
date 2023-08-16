# Web crawler weibo

 The toolbox to collect posts from https://weibo.com

![](https://shields.io/badge/dependencies-Python_3.11-blue?style=flat-square)
![](https://shields.io/badge/dependencies-Google_Chrome_≥_114-blue?style=flat-square)
![](https://shields.io/badge/tests-Google_Chrome_117_✔-brightgreen?style=flat-square)
![](https://shields.io/badge/OS-Windows_10_64--bit-lightgray?style=flat-square)

## Debug

**Linux system**

You should get cookies with Google Chrome in Windows. After finishing `login_windows.py`, you can copy this program **and the generated database** to a Linux machine and retrieve posts before the cookies expire.

Contribution is open to Linux and other operation systems and browsers' login scripts.

**Reasons for empty results**

1. Searching non-Chinese strings will usually return nothing, because "Weibo" is a Chinese social media. 
2. There are several hours' delay before posts appear in the search engine. It's better to search posts 2 days ago.

## Minimum example

Search posts containing "GitHub" at 11:00-12:00 (UTC+8) on August 15, 2023. Retrieve at most 2 pages (10 posts per page).

Run the following command.

```bash
pip install -r requirements.txt
python login_windows.py
python search.py --query="GitHub" --start_time=2023-08-15-11 --end_time=2023-08-15-12 --max_page=2
```

If you find errors or need customization, please read the "usage" section.

## Usage

In the minimum example, I assume the computer has installed Google Chrome in the default path. If Google Chrome is installed, but in the customized path, please run the following command and set `chrome_user_data` manually.

```
python login_windows.py --help
```

For more search options, see

```bash
python search.py --help
```

If the database path is by default, the results are saved in `posts.db` database.

View the `search` table and get the table name. The data structure is shown as follows.

| Name       | Type | Description                                                  |
| ---------- | ---- | ------------------------------------------------------------ |
| query      | text | The searching words.                                         |
| start_time | text | Posts from this hour will be collected. The [format code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) is %Y-%m-%d-%H |
| end_time   | text | Posts till this hour will be collected. The format is the same as `start_time` |
| table      | text | The table name that this query's results are stored.         |

According to this table name, view the results in the mentioned table.


The data structure of the search results:

| Name        | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| avatar      | text | Link to the avatar of the post author.                       |
| nickname    | text | Username of the post author.                                 |
| user_id     | text | User ID of the post author.                                  |
| posted_time | text | The time when the post was published. Its format can be either seconds/hours/days ago (in Chinese) or an exact datetime with or without years. |
| source      | text | How the post author visits "weibo". It can be either the device name or the topic (tag) name. |
| weibo_id    | text |                                                              |
| content     | text | The main body of the post. This column of fast reposts will be empty. |
| reposts     | text | Number of reposts. Chinese character "万" may appear in this field, as well as `comments` and `likes`, which means "muptiply 10,000". |
| comments    | text | Number of comments.                                          |
| likes       | text | Number of likes.                                             |

SQL statements:

<table>
<thead>
<tr><th>Name</th><th>Table</th><th>Description</th></tr>
</thead>
<tbody>
    <tr>
        <td>User profile URL</td>
        <td>search results</td>
        <td><code>'https://weibo.com/u/' || user_id</code></td>
    </tr>
    <tr>
        <td>Post URL</td>
        <td>search results</td>
        <td><code>'https://weibo.com/' || user_id || '/' || weibo_id</code></td>
    </tr>
</tbody>
</table>
