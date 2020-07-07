#!/usr/local/bin/python3
import os.path
import pickle
import requests
import hashlib

headers = {'User-Agent': 'Img2Commons'}
api_url = 'https://commons.wikimedia.org/w/api.php'
  
def get_edit_token(cookies):
  edit_token_response=requests.post(api_url, data={'action': 'query','format': 'json','meta': 'tokens'}, cookies=cookies)
  return edit_token_response.json()['query']['tokens']['csrftoken']
  
def login(username, password):
  # get login token
  payload = {'action': 'query', 'format': 'json', 'utf8': '', 'meta': 'tokens', 'type': 'login'}
  r1 = requests.post(api_url, data=payload)
  login_token=r1.json()['query']['tokens']['logintoken']

  # use login token to log in
  login_payload = {'action': 'login', 'format': 'json', 'utf8': '','lgname': username, 'lgpassword': password, 'lgtoken': login_token}
  r2 = requests.post(api_url, data=login_payload, cookies=r1.cookies)

  # return response
  return r2.cookies.copy()

def exists(image_remote_filename):
  response = requests.get(api_url + "?action=query&format=json&titles=File:" + image_remote_filename)
  return '-1' not in response.json()['query']['pages']

def checkHashOnRemote(hash_of_file):
  response = requests.get(api_url + "?action=query&format=json&list=allimages&aisha1=" + hash_of_file)
  return not not response.json()['query']['allimages']

def upload(image_local_filename, image_remote_filename, meta_text, session_cookie, comment):
  files={'file': (image_remote_filename, open(image_local_filename,'rb'), 'multipart/form-data')}

  upload_payload={
    'action': 'upload',
    'format': 'json',
    'filename': image_remote_filename,
    'comment': comment,
    'text': meta_text,
    'token': get_edit_token(session_cookie),
    "ignorewarnings": 1}

  return requests.post(api_url, data=upload_payload, files=files, cookies=session_cookie, headers=headers)

def getHashOfFile(filename):
  h = hashlib.sha1()

  # open file for reading in binary mode
  with open(filename,'rb') as file:

    # loop till the end of the file
    chunk = 0
    while chunk != b'':
      # read only 1024 bytes at a time
      chunk = file.read(1024)
      h.update(chunk)

  # return the hex representation of digest
  return h.hexdigest()
   
def getAllFilesInCategory(category):
  cmcontinue = ''
  result = []

  while True: 
    base_url = api_url + '?action=query&list=categorymembers&'\
              'cmtype=file&cmtitle=Category:'+category+'&'\
              'cmlimit=max&format=json&cmcontinue=' + cmcontinue
    
    response = requests.get(base_url + cmcontinue)
    data = response.json()

    if not 'continue' in data:
      return result

    cmcontinue = data['continue']['cmcontinue']

    for i in data['query']['categorymembers']:
      result.append(i['title'])
