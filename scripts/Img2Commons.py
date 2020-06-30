#!/usr/local/bin/python3
import json,sys,os,argparse
from CommonsUpload import login, exists, existsHashOfFile, upload
import pandas
from liquid import Liquid
from datetime import datetime

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Uploads images in batch to Wikimedia Commons')
  parser.add_argument('--csv',help="input csv file", required=True)
  parser.add_argument('--metadata',help="metadata template", required=True)
  parser.add_argument('--local-image',help="local image template", required=True)
  parser.add_argument('--remote-image',help="remote image template", required=True)
  parser.add_argument('--login',nargs=2,help="username password", required=True)
  parser.add_argument('--rows',nargs=2,help="start-row end-row")
  # response = login(sys.argv[1], sys.argv[2], "session")

  parser.add_argument('action', choices=['test', 'upload'])
  parser.add_argument('--verbose', '-v', action='count', default=0)
  args = parser.parse_args()

print(datetime.now().strftime("%H:%M:%S"))

# login
if args.login:
  print("Login...")
  session_cookie = login(args.login[0],args.login[1])

# read csv
print("Load CSV...")
csv_df = pandas.read_csv(args.csv)
csv_df.fillna("", inplace=True) #fill empty cells with ""
csv_dict=csv_df.to_dict(orient='records')

# read templates
print("Load templates...")
liq_meta = Liquid(args.metadata, liquid_from_file=True) 
liq_local = Liquid(args.local_image, liquid_from_file=True) 
liq_remote = Liquid(args.remote_image, liquid_from_file=True) 

#select rows
if args.rows:
  begin=int(args.rows[0])
  end=int(args.rows[1])
else:
  begin=0
  end=len(csv_dict)

# for each record
for i in range(begin,end):
  try:
    row = csv_dict[i]
    metadata = liq_meta.render(**row)
    metadata = metadata.replace("{_","{{")
    metadata = metadata.replace("_}","}}")

    local_filename = liq_local.render(**row)
    remote_filename = liq_remote.render(**row)
    
    print("#"+str(i+2)+":",os.path.basename(local_filename), "->", remote_filename)

    if existsHashOfFile(local_filename):
      print("Skip: Hash of file exists")
      continue      

    if exists(remote_filename):
      print("Skip: Filename Exists")
      continue

    if args.action=='test':
      print(metadata)

    elif args.action=='upload':
      response = upload(local_filename, remote_filename, metadata, session_cookie);
      
      data = response.json()

      if 'error' in data and 'code' in data['error']:
        print("Upload Error",data['error']['code'],data['error']['info'])

        if data['error']['code']=="ratelimited":   #stop trying and quit on this error
          print(datetime.now().strftime("%H:%M:%S"))
          sys.exit()

      elif 'upload' in data and 'result' in data['upload']: 
        print(data['upload']['result']+":",data['upload']['imageinfo']['descriptionurl'])

        if 'warnings' in data['upload']:
          print(data['upload']['warnings'])

      else:
        print(json.dumps(data, indent=4, sort_keys=True))

  except OSError as err:
    print("OS Error: Skipping line",i+2,err)
    pass

print(datetime.now().strftime("%H:%M:%S"))



