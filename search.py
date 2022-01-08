import os
from datetime import datetime
from urllib.parse import quote
import pandas as pd
from requests import Session
from bs4 import BeautifulSoup
import re
from time import sleep
from random import random

search_string = ''
start_time = datetime(year=2022, month=1, day=1, hour=0)
end_time = datetime(year=2022, month=1, day=1, hour=6)
rest_time = [2, 5]  # interval between two requests

if not os.path.exists('cached/weibo_cookies.pkl'):
    from login import *
    print('Open your Google Chrome browser and visit https://weibo.com \n'
          'Keep the tab open, and press any key to continue ...')
    os.system('pause')
    save_cookies()
    print('Now, you can close Google Chrome. Press any key to continue ...')
    os.system('pause')
cookies = pd.read_pickle('cached/weibo_cookies.pkl')
cookies = dict(zip(cookies.name, cookies.value))
cookies = '; '.join([f'{k}={v}' for k, v in cookies.items()])

sess = Session()
sess.trust_env = False

url = f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&timescope=custom:" \
      f"{start_time.strftime('%Y-%m-%d')}-{start_time.hour}:{end_time.strftime('%Y-%m-%d')}-{end_time.hour}&Refer=g"
chrome_96 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6",
    "Connection": "keep-alive",
    "Cookie": cookies,
    "DNT": "1",
    "Host": "s.weibo.com",
    "Referer": url,
    "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/97.0.4692.71 Safari/537.36"
}
response = sess.get(url, headers=chrome_96, verify=True)
sleep(round(rest_time[0] + random() * (rest_time[1] - rest_time[0]), 1))
response = BeautifulSoup(response.text, features='html.parser')
if not response:
    raise Exception(f'No access to searching results: {search_string}, {start_time}~{end_time}.')
max_page = response.find('ul', {'node-type': 'feed_list_page_morelist', 'action-type': 'feed_list_page_morelist'})
if max_page:
    max_page = len(max_page.find_all('li'))
else:
    max_page = 1

print(f'{search_string}, {start_time}~{end_time}, {max_page} pages in total.')
posts_df = pd.DataFrame(columns=['avatar', 'nickname', 'homepage', 'posted_time', 'source', 'content', 'images',
                                 'reposts', 'comments', 'likes'])
posts = response.find_all('div', {'class': 'card-wrap', 'action-type': 'feed_list_item'})
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
    try:
        attributes['images'] = [x.get('src') for x in
                                post.find('div', {'node-type': 'feed_list_media_prev'}).find_all('img')]
    except AttributeError:
        pass
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
    posts_df = posts_df.append(attributes, ignore_index=True)
print(f'Successfully collected: {search_string}, {start_time}~{end_time}, page=1.')

for page in range(2, max_page + 1):
    url = f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&timescope=custom:" \
          f"{start_time.strftime('%Y-%m-%d')}-{start_time.hour}:{end_time.strftime('%Y-%m-%d')}-{end_time.hour}&" \
          f"Refer=g&page={page}"
    chrome_96['Referer'] = url
    response = sess.get(url, headers=chrome_96, verify=True)
    sleep(round(rest_time[0] + random() * (rest_time[1] - rest_time[0]), 1))
    response = BeautifulSoup(response.text, features='html.parser')
    if not response:
        print(f'Cannot parse this page: {search_string}, {start_time}~{end_time}, page={page}.')
        continue
    posts = response.find_all('div', {'class': 'card-wrap', 'action-type': 'feed_list_item'})
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
        try:
            attributes['images'] = [x.get('src') for x in
                                    post.find('div', {'node-type': 'feed_list_media_prev'}).find_all('img')]
        except AttributeError:
            pass
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
        posts_df = posts_df.append(attributes, ignore_index=True)
    print(f'Successfully collected: {search_string}, {start_time}~{end_time}, page={page}.')

if not os.path.exists('results'):
    os.mkdir('results')
posts_df.to_pickle(f'results/weibo-{search_string}-{int(start_time.timestamp())}-{int(end_time.timestamp())}.pkl')
