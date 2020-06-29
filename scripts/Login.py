#!/usr/local/bin/python3
import json
import sys
from CommonsUpload import login

if len(sys.argv)<3:
  print('Login to Wikimedia Commons. A session Cookie file will be stored in the current folder.')
  print('Usage: ./login.py You@YourBot fake013ujvjnii394ol0password')
  sys.exit(1)

response = login(sys.argv[1], sys.argv[2], "session")

print(json.dumps(response.json(), indent=4, sort_keys=True))

