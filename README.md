# "weibo.com" Web Crawler

 A web crawler for "weibo.com" posts

![](https://shields.io/badge/OS-Microsoft%20Windows%2010%2064--bit-lightgray.svg)
![](https://shields.io/badge/dependencies-Google%20Chrome%20>=%2096-blue.svg)
![](https://shields.io/badge/dependencies-Python%203.9-blue.svg)
![](https://shields.io/badge/tests-Google%20Chrome%2096%20✔-brightgreen.svg)

## Introduction

This script helps collect attributes of posts at "weibo.com". Users can record posts in different lists (or flows, or collections), like the searching results. The supported lists (or flows, or collections) are listed in "Functions" section.

## Usage

Run

```bash
pip install -r requirements.txt
```

Login "weibo.com" in browser, and don't close the browser. 

Then, if you installed Google Chrome in default folder, run `login_windows.py`. Otherwise, you will find it useful to modify Line 34 and 37. Please assign these two variables to cookies and encryption key respectively.

After that, close the browser.

Now, it's free to use functions listed below.

## Functions

### 1.  Search for posts

**Filename:** `search.py`

**Description:** This script searches for a word and a specific time period.  It records all the searching result in SQLite database.

**Parameters:**

| Name            | Description                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------- |
| `search_string` | The string to search for. All posts containing this string will be recorded, 50 pages at most. |
| `start_time`    | Only posts which are posted after this time will be recorded. (Accurate to hour level)         |
| `end_time`      | Only posts which are posted before this time will be recorded. (Accurate to hour level)        |
| `rest_time`     | The interval between two requests, where the unit is second.                                   |

Results are saved in SQLite database `posts.sqlite`.
