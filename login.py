"""
Login from Google Chrome, Microsoft Windows
"""
import os
import pandas as pd
import sqlite3
import base64
from Crypto.Cipher import AES
import ctypes
import ctypes.wintypes
import json


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


if 'USERNAME' not in os.environ:
    raise Exception('Cannot obtain the current logged username in Microsoft Windows.')
username = os.environ.get('USERNAME')
cookie_file = rf'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies'
if not os.path.exists(cookie_file):
    raise Exception('Google Chrome\'s cookie file does not exist.')
encryption_key_file = rf'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Local State'
if not os.path.exists(encryption_key_file):
    raise Exception('Google Chrome\'s encryption key file does not exist.')

with open(encryption_key_file, 'r') as f:
    encrypt_key_config = json.load(f)
encrypted_key = encrypt_key_config['os_crypt']['encrypted_key']
encrypted_key = base64.b64decode(encrypted_key)
encrypted_key = encrypted_key[5:]
decrypted_key = dpapi_decrypt(encrypted_key)


def cookies_decrypt(encrypted):
    nonce, ciphertext, tag = encrypted[3:15], encrypted[15:-16], encrypted[-16:]
    cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('ascii')


def chrome_utc_parser(chrome_utc):
    if chrome_utc:
        real_utc = int(chrome_utc / 1e6) - 11644473600
        return pd.to_datetime(real_utc, unit='s')


def save_cookies():
    connection = sqlite3.connect(cookie_file)
    cookies = pd.read_sql_query('SELECT * FROM cookies', connection)
    cookies_weibo_related = cookies[cookies.host_key.str.contains('weibo.com')]
    cookies_weibo_cleaned = pd.DataFrame({
        'name': cookies_weibo_related['name'],
        'value': cookies_weibo_related['encrypted_value'].apply(cookies_decrypt),
        'expired_utc': cookies_weibo_related['expires_utc'].apply(chrome_utc_parser),
    })
    if not os.path.exists('cached'):
        os.mkdir('cached')
    cookies_weibo_cleaned.to_pickle('cached/weibo_cookies.pkl')


if __name__ == '__main__':
    save_cookies()
