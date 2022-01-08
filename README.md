# "weibo.com" Web Crawler

 A web crawler for recording posts in "sina weibo"

![](https://shields.io/badge/OS-Microsoft%20Windows%2010%2064--bit-lightgray)
![](https://shields.io/badge/dependencies-Google%20Chrome%20>=%2096-blue)
![](https://shields.io/badge/dependencies-Python%203.9-blue)
![](https://shields.io/badge/tests-Google%20Chrome%2096%20✔-brightgreen)

## Introduction

This script helps collect attributes of posts in "sina weibo". Users can record posts in different lists (or flows, or collections), like the searching results. The supported lists (or flows, or collections) are listed in "Functions" section.

## Functions

Scripts currently available:

### 1.  search

**Description:**

Search for a word and specific time interval and record all posts, the search result.

**Parameters:**

| Name            | Description                                                                                                                                                                 |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_string` | The string to search for. All posts containing this string will be recorded, 50 pages at most.                                                                              |
| `start_time`    | Only posts which are posted after this time will be recorded. (Accurate to hour level)                                                                                      |
| `end_time`      | Only posts which are posted before this time will be recorded. (Accurate to hour level)                                                                                     |
| `rest_time`     | The interval between two requests, where the unit is second.<br />Results are saved as Python pickle format at `results/weibo-{search_string}-{start_time}-{end_time}.pkl`. |
|                 |                                                                                                                                                                             |

**Notes:**

The `start_time` and `end_time` in filename are formatted as Unix timestamp (the unit is second). 

## Installation

1. Run `pip install -r requirements.txt`.
2. According to "Function" section, find the script you need.
3. Edit parameters at the head of the script.
4. Run the script with Python.

