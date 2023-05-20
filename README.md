# "weibo.com" Web Crawler

 The toolbox to collect posts from https://weibo.com

![](https://shields.io/badge/OS-Windows_10_64--bit-lightgray)
![](https://shields.io/badge/dependencies-Google_Chrome>=96-blue)
![](https://shields.io/badge/dependencies-Python_3.11-blue)
![](https://shields.io/badge/tests-Google_Chrome_113_✔-brightgreen)

## Usage

1. Run the following script.
   ```bash
   pip install -r requirements.txt
   ```

2. Login https://weibo.com/ in Google Chrome, and don't close it. <br>
   *We assume Google Chrome is installed in default path. Otherwise, please modify Line 34 and 37 and assign these two variables to your customized cookies and encryption key respectively.*

3. Run `login_windows.py`. By default, it creates a database at `posts.db`. *The file path can be customized with `db` argument. [Detail](docs/login_windows.md)*

4. Close the browser.

5. The following functions work for you now.

## Functions

[login_windows](docs/login_windows.md)

Log in https://weibo.com and save logged-in status, with Windows platform.

[search](docs/search.md)

Searches for a word and a specific time period.  It records all the searching result in SQLite database.
