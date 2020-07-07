#!/usr/local/bin/python3
import requests,json,re

# category = 'Images from Het Utrechts Archief'
category = 'Deelcollectie Nederlandse-Spoorwegen'
cmcontinue = ''

while True: 
  base_url = 'https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&'\
            'cmtype=file&cmtitle=Category:'+category+'&'\
            'cmlimit=max&format=json&cmcontinue=' + cmcontinue

  response = requests.get(base_url + cmcontinue)
  data = response.json()

  for i in data['query']['categorymembers']:
    print(i['title'])

  if 'continue' in data:
    cmcontinue = data['continue']['cmcontinue']
  else: 
    break
