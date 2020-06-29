#!/usr/local/bin/python3
import os.path
import pickle
import requests

headers = {'User-Agent': 'Img2Commons'}
api_url = 'https://commons.wikimedia.org/w/api.php'
  
def get_edit_token(cookies):
  edit_token_response=requests.post(api_url, data={'action': 'query','format': 'json','meta': 'tokens'}, cookies=cookies)
  return edit_token_response.json()['query']['tokens']['csrftoken']

def load_cookies(filename):
  with open(filename, 'rb') as f:
    return pickle.load(f)

def save_cookies(filename, cookies):
  with open(filename, 'wb') as f:
    pickle.dump(cookies, f)

def login(username, password, session_file_name="session"):
  # get login token
  payload = {'action': 'query', 'format': 'json', 'utf8': '', 'meta': 'tokens', 'type': 'login'}
  r1 = requests.post(api_url, data=payload)
  login_token=r1.json()['query']['tokens']['logintoken']

  # use login token to log in
  login_payload = {'action': 'login', 'format': 'json', 'utf8': '','lgname': username, 'lgpassword': password, 'lgtoken': login_token}
  r2 = requests.post(api_url, data=login_payload, cookies=r1.cookies)

  # save cookies
  save_cookies(session_file_name, r2.cookies)

  # return response
  return r2

def upload(image_local_filename, image_remote_filename, meta_text, session_file_name="session"):
  files={'file': (image_remote_filename, open(image_local_filename,'rb'), 'multipart/form-data')}

  cookies = load_cookies(session_file_name)

  upload_payload={'action': 'upload',
    'format': 'json',
    'filename': image_remote_filename,
    'comment': 'Img2Commons',
    'text': meta_text,
    'token': get_edit_token(cookies),
    "ignorewarnings": 1}

  return requests.post(api_url, data=upload_payload, files=files, cookies=cookies, headers=headers)

