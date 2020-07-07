#!/usr/local/bin/python3
import json,sys,os,argparse,time
from CommonsUpload import login, exists, getHashOfFile, checkHashOnRemote, upload
import pandas
from liquid import Liquid
from datetime import datetime

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Uploads images in batch to Wikimedia Commons')
  parser.add_argument('--csv',help="input csv file", required=True)
  parser.add_argument('--metadata',help="metadata template", required=True)
  parser.add_argument('--local-image',help="local image template", required=True)
  parser.add_argument('--remote-image',help="remote image template", required=True)
  parser.add_argument('--comment',help="upload summary/comment template", required=True)
  parser.add_argument('--login',nargs=2,help="username password", required=True)
  parser.add_argument('--hash-log',help="text file with hashes to skip (and to append to)")
  parser.add_argument('--name-log',help="text file with remote filenames to skip")
  parser.add_argument('--rows',nargs=2,help="start-row end-row")
  parser.add_argument('--resume-file',help="filename containing number where to continue when restarting")

  parser.add_argument('action', choices=['test', 'upload'])
  parser.add_argument('--verbose', '-v', action='count', default=0)
  args = parser.parse_args()

print(datetime.now().strftime("%H:%M:%S"))

# login
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
liq_comment = Liquid(args.comment, liquid_from_file=True) 

print("Load name-log: remote filenames to skip...")
if args.name_log:
  with open(str(args.name_log), "r") as file:
    name_log = file.read().splitlines()

print("Load name-log: remote filenames to skip...")
if args.hash_log:
  with open(str(args.hash_log), "r") as file:
    hash_log = file.read().splitlines()

#select rows
if args.rows:
  begin=int(args.rows[0])
  end=min(int(args.rows[1]),len(csv_dict))
elif args.resume_file:
  with open(str(args.resume_file), "r") as file:
    begin = int(file.readline())
  end=len(csv_dict)
else:
  begin=0
  end=len(csv_dict)

# for each record
for i in range(begin,end):
  sys.stdout.flush()

  if args.resume_file:
    with open(str(args.resume_file), "w") as file:
      file.write(str(i))

  try:
    row = csv_dict[i]
    metadata = liq_meta.render(**row)
    metadata = metadata.replace("{_","{{")
    metadata = metadata.replace("_}","}}")

    local_filename = liq_local.render(**row)
    remote_filename = liq_remote.render(**row)
    comment = liq_comment.render(**row)
    
    print("#"+str(i+2)+":",os.path.basename(local_filename), "->", remote_filename)

    if remote_filename in name_log:
      print("Skip: File on list with remote filenames to skip")
      if args.action=='upload':
        continue

    if args.hash_log:
      if getHashOfFile(local_filename) in hash_log:
        print("Skip: File on list with hashes to skip")
        if args.action=='upload':
          continue  

    if checkHashOnRemote(getHashOfFile(local_filename)):
      print("Skip: Hash of file exists on remote")
      
      if args.hash_log:
        with open(str(args.hash_log), "a") as file:   # add the hash to the list
          file.write(getHashOfFile(local_filename) + "\n")

      if args.action=='upload':
        continue      

    if exists(remote_filename):
      print("Skip: Remote filename exists")
      if args.action=='upload':
        continue

    if args.action=='test':
      print("Upload summary:",comment)
      print(metadata)

    elif args.action=='upload':
      response = upload(local_filename, remote_filename, metadata, session_cookie, comment);
      
      data = response.json()

      if 'error' in data and 'code' in data['error']:
        print("Upload Error",data['error']['code'],data['error']['info'])

        if data['error']['code']=="ratelimited":
          print(datetime.now().strftime("%H:%M:%S"))
          print("Waiting 15 minutes to continue...")
          sys.stdout.flush()
          time.sleep(15*60)
          print("Login...")
          session_cookie = login(args.login[0],args.login[1])
          # FIXME: it should try the last one again instead going to the next
          # i=i-1 #try the last one again

      elif 'upload' in data and 'result' in data['upload']: 
        print(data['upload']['result']+":",data['upload']['imageinfo']['descriptionurl'])

        if 'warnings' in data['upload']:
          print(data['upload']['warnings'])

      else:

# with open(hash_log, "a") as file:
        # file.write(getHashOfFile(local_filename))


        print(json.dumps(data, indent=4, sort_keys=True))

    # print("Wait 5 seconds")
    # time.sleep(5)

  except OSError as err:
    print("OS Error: Skipping line",i+2,err)
    pass

print(datetime.now().strftime("%H:%M:%S"))



