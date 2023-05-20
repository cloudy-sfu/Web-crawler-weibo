import random
import re
import sqlite3
from time import sleep
from urllib.parse import quote
import pandas as pd
from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm

sess = Session()
sess.trust_env = False


def get_first_page(search_string, header, st, et, rest_time=(2, 5)):
    url = f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&timescope=custom%3A" \
          f"{st[0]}-{st[1]}-{st[2]}-{st[3]}%3A{et[0]}-{et[1]}-{et[2]}-{et[3]}&Refer=g"
    response = sess.get(url, headers=header, verify=True)
    assert response.status_code == 200, f'Response code is {response.status_code} for {url}'
    sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
    response = BeautifulSoup(response.text, features='html.parser')
    assert response, f'Cannot parse webpage {url}'
    max_page = response.find('ul', {'node-type': 'feed_list_page_morelist', 'action-type': 'feed_list_page_morelist'})
    max_page = len(max_page.find_all('li')) if max_page else 1
    return response, max_page


def get_subseq_page(search_string, header, st, et, page, rest_time=(2, 5)):
    url = f"https://s.weibo.com/weibo?q={quote(search_string)}&typeall=1&suball=1&timescope=custom:" \
          f"{st[0]}-{st[1]}-{st[2]}-{st[3]}:{et[0]}-{et[1]}-{et[2]}-{et[3]}&Refer=g&page={page}"
    response = sess.get(url, headers=header, verify=True)
    if response.status_code != 200:
        print(f"[Warning] Fail to fetch page (response code {response.status_code}).")
        print("[Warning] ", url)
        return
    sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
    response = BeautifulSoup(response.text, features='html.parser')
    if not response:
        print("[Warning] Fail to parse page.")
        print("[Warning] ", url)
        return
    return response


def get_posts(web_text, header, db, table, rest_time=(2, 5)):
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
            # profile https://weibo.com/u/$user_id
            attributes['user_id'] = post.find('a', {'class': 'name'}).get('href').split('/')[-1].split('?')[0]
        except AttributeError:
            pass
        try:
            attributes['posted_time'] = post.find('a', {'suda-data': re.compile('wb_time')}).text.strip()
        except AttributeError:
            pass
        try:
            attributes['source'] = post.find('a', {'rel': 'nofollow'}).text.strip()
        except AttributeError:
            pass
        try:
            # post https://weibo.com/$user_id/$weibo_id
            attributes['weibo_id'] = post.find('a', text=re.compile('复制微博地址')).get(
                '@click', '').split('/')[-1].split('?')[0]
        except AttributeError:
            pass
        try:
            unfold_link = post.find('a', {'action-type': "fl_unfold"})
            if unfold_link and 'weibo_id' in attributes.keys():
                response = sess.get(url="https://weibo.com/ajax/statuses/longtext", headers=header, verify=True,
                                    params={'id': attributes['weibo_id']})
                sleep(round(random.uniform(rest_time[0], rest_time[1]), 2))
                if response.status_code == 200:
                    attributes['content'] = response.json().get('data').get('longTextContent')
        except AttributeError:
            pass
        if 'content' not in attributes.keys():
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
            reposts = post.find('a', {'action-type': 'feed_list_forward'}).text.strip()
            attributes['reposts'] = "0" if reposts == "转发" else reposts
        except AttributeError:
            pass
        try:
            comments = post.find('a', {'action-type': 'feed_list_comment'}).text.strip()
            attributes['comments'] = "0" if comments == "评论" else comments
        except AttributeError:
            pass
        try:
            likes = post.find('span', {'class': 'woo-like-count'}).text.strip()
            attributes['likes'] = "0" if likes == "赞" else likes
        except AttributeError:
            pass
        posts_df.append(attributes)
    posts_df = pd.DataFrame(data=posts_df,
                            columns=['avatar', 'nickname', 'user_id', 'posted_time', 'source', 'weibo_id', 'content',
                                     'reposts', 'comments', 'likes'])
    connection = sqlite3.connect(db)
    posts_df.to_sql(table, connection, if_exists='append', index=False)
    connection.close()


def search(db, table, query, start_time, end_time, max_page=None):
    connection = sqlite3.connect(db)
    cookies = pd.read_sql_query('select * from cookies', connection)
    connection.close()

    cookies = dict(zip(cookies.name, cookies.value))
    cookies = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    chrome_113 = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7", "cache-control": "max-age=0",
        "cookie": cookies, "dnt": "1",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
        "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36"
    }
    response, existed_page = get_first_page(
        search_string=query, header=chrome_113, st=start_time, et=end_time)
    if max_page:
        max_page = min(max_page, existed_page)
    else:
        max_page = existed_page
    get_posts(db=db, table=table, header=chrome_113, web_text=response)
    pbar = tqdm(total=max_page)
    pbar.update(1)
    for page in range(2, max_page + 1):
        response = get_subseq_page(search_string=query, header=chrome_113, st=start_time, et=end_time, page=page)
        if response:
            get_posts(db=db, table=table, header=chrome_113, web_text=response)
        pbar.update(1)
    pbar.close()
