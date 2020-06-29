#!/usr/local/bin/python3
import json
import sys
from CommonsUpload import upload

if len(sys.argv)<3:
  print('Usage: ./upload.py IMAGE_FILE META_FILE')
  sys.exit(1)

image_file_name = sys.argv[1]
meta_text = open(sys.argv[2], "r").read()

response = upload(image_file_name, meta_text, "session")

print(json.dumps(response.json(), indent=4, sort_keys=True))
