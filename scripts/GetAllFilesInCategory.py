#!/usr/local/bin/python3
# import requests,json,re

# category = 'Images from Het Utrechts Archief'
from CommonsUpload import getAllFilesInCategory 

for i in getAllFilesInCategory('Collection Nederlandse-Spoorwegen from Het Utrechts Archief'):
  print(i)

