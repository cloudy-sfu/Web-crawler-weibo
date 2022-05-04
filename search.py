import re
import sqlite3
from datetime import datetime
from random import random
from time import sleep
from urllib.parse import quote
from warnings import warn

import pandas as pd
from bs4 import BeautifulSoup
from requests import Session

connection = sqlite3.connect('posts.sqlite')
cookies = pd.read_sql_query('select * from cookies', connection)
cookies = dict(zip(cookies.name, cookies.value))
cookies = '; '.join([f'{k}={v}' for k, v in cookies.items()])

sess = Session()
sess.trust_env = False
chrome_101 = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                        "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "accept-encoding": "gzip, deflate, br",
              "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7", "cache-control": "max-age=0",
              "cookie": cookies, "dnt": "1",
              "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
              "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "document",
              "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1",
              "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                              "Chrome/101.0.4951.54 Safari/537.36"}


def query_weibo(search_string, start_time, end_time, page_=1, rest_time=(2, 5)):
    url = f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&timescope=custom:" \
          f"{start_time.strftime('%Y-%m-%d')}-{start_time.hour}:{end_time.strftime('%Y-%m-%d')}-{end_time.hour}&Refer=g"
    if page_ > 1:
        url += f"&page={page_}"
    response_ = sess.get(url, headers=chrome_101, verify=True)
    if response_.status_code != 200:
        warn(f'Response code is {response_.status_code} for {url}')
        return False, None, None
    sleep(round(rest_time[0] + random() * (rest_time[1] - rest_time[0]), 1))
    response_ = BeautifulSoup(response_.text, features='html.parser')
    if not response_:
        warn(f'Cannot parse webpage for {url}')
        return False, None, None
    if page_ == 1:
        max_page_ = response_.find('ul', {'node-type': 'feed_list_page_morelist',
                                          'action-type': 'feed_list_page_morelist'})
        max_page_ = len(max_page_.find_all('li')) if max_page_ else 1
        return True, response_, max_page_
    return True, response_, None


def get_posts(table_name, web_text):
    posts = web_text.find_all('div', {'class': 'card-wrap', 'action-type': 'feed_list_item'})
    posts_df = []
    for post in posts:
        attributes = dict()
        try:
            attributes['avatar'] = post.find('div', {'class': 'avator'}).find('img').get('src')
        except AttributeError:
            pass
        try:
            attributes['nickname'] = post.find('a', {'class': 'name'}).get('nick-name')
        except AttributeError:
            pass
        try:
            attributes['homepage'] = post.find('a', {'class': 'name'}).get('href')
        except AttributeError:
            pass
        try:
            attributes['posted_time'] = post.find('p', {'class': 'from'}).find('a', {'suda-data': True}).text.strip()
        except AttributeError:
            pass
        try:
            attributes['source'] = post.find('a', {'rel': 'nofollow'}).text.strip()
        except AttributeError:
            pass
        try:
            attributes['content'] = post.find('p', {'class': 'txt', 'node-type': 'feed_list_content'}).text.strip()
            attributes['content'] = re.sub('\u200b', '', attributes['content'])
            attributes['content'] = re.sub('\ue627', '', attributes['content'])
        except AttributeError:
            pass
        # SQLite 3 doesn't support list
        # try:
        #     attributes['images'] = [x.get('src') for x in
        #                             post.find('div', {'node-type': 'feed_list_media_prev'}).find_all('img')]
        # except AttributeError:
        #     pass
        try:
            attributes['reposts'] = post.find('a', {'action-type': 'feed_list_forward'}).text
        except AttributeError:
            pass
        try:
            attributes['comments'] = post.find('a', {'action-type': 'feed_list_comment'}).text
        except AttributeError:
            pass
        try:
            attributes['likes'] = post.find('span', {'class': 'woo-like-count'}).text
        except AttributeError:
            pass
        posts_df.append(attributes)
    posts_df = pd.DataFrame(data=posts_df,
                            columns=['avatar', 'nickname', 'homepage', 'posted_time', 'source', 'content',
                                     'reposts', 'comments', 'likes'])
    posts_df.to_sql(table_name, connection, if_exists='append', index=False)


if __name__ == '__main__':
    flag, response, max_page = query_weibo(
        search_string='原神',
        start_time=datetime(year=2022, month=5, day=1, hour=3),
        end_time=datetime(year=2022, month=5, day=1, hour=6),
    )
    if flag:
        get_posts(table_name='Genshin', web_text=response)
        print("Finish reading page 1")
        for page in range(2, max_page + 1):
            flag, response, _ = query_weibo(
                search_string='原神',
                start_time=datetime(year=2022, month=5, day=1, hour=3),
                end_time=datetime(year=2022, month=5, day=1, hour=6),
                page_=page
            )
            if not flag:
                continue
            get_posts(table_name='Genshin', web_text=response)
            print("Finish reading page", page)
