"""
Login from Google Chrome, Microsoft Windows
"""
import os
import pandas as pd
import sqlite3
import base64
from Crypto.Cipher import AES
import ctypes
import json
from argparse import ArgumentParser
from selenium import webdriver
import psutil

parser = ArgumentParser()
parser.add_argument('--chrome_user_data', type=str,
                    help='The \'User Data\' file under the installation path of Google Chrome. If blank, assume'
                         'Google Chrome\'s installed at default directory.')
parser.add_argument('--db', type=str, default='./posts.db',
                    help='The path of the database, where to store the cookies and fetched posts. If blank, data is '
                         'saved at posts.db of this program\'s root directory.')
command, _ = parser.parse_known_args()

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
        if chrome_user_data is None:
            username = os.environ.get('USERNAME')
            if username is None:
                raise Exception('[Error] Cannot obtain the current logged user\'s username in Microsoft Windows.')
            chrome_user_data = rf'C:\Users\{username}\AppData\Local\Google\Chrome\User Data'
        self.cookie_file = os.path.join(chrome_user_data, r'Default\Network\Cookies')
        encryption_key_file = os.path.join(chrome_user_data, r'Local State')
        if not os.path.exists(self.cookie_file):
            raise Exception('[Error] Google Chrome\'s cookie file does not exist.')
        if not os.path.exists(encryption_key_file):
            raise Exception('[Error] Google Chrome\'s encryption key file does not exist.')

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
        cookies = pd.read_sql(sql="SELECT * FROM cookies WHERE host_key LIKE '%weibo.com%'", con=c)
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
    # confirm Google Chrome is closed.
    chrome_opened = True
    while chrome_opened:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == 'chrome.exe':
                _ = input('[Info] Google Chrome is already open. Please close Google Chrome and press "Enter" to '
                          'continue.')
                break
        else:
            chrome_opened = False

    # guide users to get cookies.
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--disable-features=LockProfileCookieDatabase')
    chrome = webdriver.Chrome(options=chrome_option)
    chrome.get('file:///' + os.path.abspath('chrome_instruction.html'))
    _ = input('[Info] Press "Enter" to continue.')
    weibo_client = WeiboClient(**vars(command))
    weibo_client.login()
    chrome.quit()
