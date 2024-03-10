"""
Login from Google Chrome, Microsoft Windows
"""
import base64
import ctypes
import json
import logging
import os
import sqlite3
import subprocess
import sys

import pandas as pd
import psutil
from Crypto.Cipher import AES

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)


def dpapi_decrypt(encrypted):
    class DataBlob(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blob_in = DataBlob(ctypes.sizeof(p), p)
    blob_out = DataBlob()
    ret = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out))
    if not ret:
        raise ctypes.WinError()
    result = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return result


def chrome_utc_parser(chrome_utc):
    if chrome_utc:
        real_utc = int(chrome_utc / 1e6) - 11644473600
        return pd.to_datetime(real_utc, unit='s')


class WeiboClient:
    def __init__(self, db, chrome_user_data):
        self.cookie_file = os.path.join(chrome_user_data, r'Default\Network\Cookies')
        encryption_key_file = os.path.join(chrome_user_data, r'Local State')
        if not os.path.exists(self.cookie_file):
            raise Exception('[Error] Google Chrome\'s cookie file does not exist.')
        if not os.path.exists(encryption_key_file):
            raise Exception(
                '[Error] Google Chrome\'s encryption key file does not exist.')

        with open(encryption_key_file, 'r') as f:
            encrypt_key_config = json.load(f)
        encrypted_key = encrypt_key_config['os_crypt']['encrypted_key']
        encrypted_key = base64.b64decode(encrypted_key)
        encrypted_key = encrypted_key[5:]
        self.decrypted_key = dpapi_decrypt(encrypted_key)
        self.db = db

    def _cookies_decrypt(self, encrypted):
        nonce, ciphertext, tag = encrypted[3:15], encrypted[15:-16], encrypted[-16:]
        cipher = AES.new(self.decrypted_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('ascii')

    def login(self):
        # https://github.com/borisbabic/browser_cookie3/issues/180
        c = sqlite3.connect(self.cookie_file)
        cookies = pd.read_sql(
            sql="SELECT * FROM cookies WHERE host_key LIKE '%weibo.com%'", con=c)
        c.close()
        cookies_weibo_cleaned = pd.DataFrame({
            'name': cookies['name'],
            'value': cookies['encrypted_value'].apply(self._cookies_decrypt),
            'expired_utc': cookies['expires_utc'].apply(chrome_utc_parser),
        })
        c = sqlite3.connect(self.db)
        cookies_weibo_cleaned.to_sql('cookies', c, index=False, if_exists='replace')
        c.close()


if __name__ == '__main__':
    # check system environment
    username = os.environ.get('USERNAME')
    if username is None:
        raise Exception("Please confirm you are using Windows and have logged as a "
                        "Windows user. An error occured because environment variable "
                        "USERNAME doesn't have a value.")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_user_data_ = rf'C:\Users\{username}\AppData\Local\Google\Chrome\User Data'
    db_ = os.path.abspath('posts.db')

    # get arguments
    logging.info(f"Google Chrome user's data is stored at {chrome_user_data_}. If you "
                 f"have assigned a different path, please write it down. Otherwise "
                 f"press ENTER to continue.")
    chrome_user_data_input = input()
    if chrome_user_data_input is not None and os.path.isdir(chrome_user_data_input):
        chrome_user_data_ = chrome_user_data_input

    logging.info(f"The database of this program is {db_}. If you want to store this "
                 f"program's data at a different path, please write it down. Otherwise "
                 f"press ENTER to continue.")
    db_input = input()
    if db_input is not None:
        db_ = db_input

    logging.info(f"Google Chrome should be installed at {chrome_path} by default. If "
                 f"it's installed at a different path, please write it down. Otherwise "
                 f"press ENTER to continue.")
    chrome_path_input = input()
    if chrome_path_input is not None and os.path.isfile(chrome_path_input):
        chrome_path = chrome_path_input

    # confirm Google Chrome is closed
    chrome_opened = True
    while chrome_opened:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == 'chrome.exe':
                logging.info('Google Chrome is already open. Please close Google Chrome '
                             'and press ENTER to continue.')
                _ = input()
                break
        else:
            chrome_opened = False

    # guide users to get cookies
    subprocess.Popen((chrome_path, 'https://weibo.com/',
                      '--disable-features=LockProfileCookieDatabase'))
    logging.info('Please login https://weibo.com/ in the prompted Google Chrome session '
                 '(do not close the session), then press ENTER to continue. ')
    _ = input()
    weibo_client = WeiboClient(db_, chrome_user_data_)
    weibo_client.login()
    logging.info("Logged in. Please close Google Chrome.")
