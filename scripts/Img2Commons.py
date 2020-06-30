#!/usr/local/bin/python3
import json,sys,os,argparse
from CommonsUpload import login
from CommonsUpload import exists
from CommonsUpload import upload
import pandas
from liquid import Liquid

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Uploads images in batch to Wikimedia Commons')
  parser.add_argument('--csv',help="input csv file", required=True)
  parser.add_argument('--metadata',help="metadata template", required=True)
  parser.add_argument('--local-image',help="local image template", required=True)
  parser.add_argument('--remote-image',help="remote image template", required=True)
  parser.add_argument('--login',nargs=2)
  # response = login(sys.argv[1], sys.argv[2], "session")

  parser.add_argument('action', choices=['test', 'upload'])
  parser.add_argument('--verbose', '-v', action='count', default=0)
  args = parser.parse_args()

if args.login:
  print("Login...")
  response = login(args.login[0],args.login[1],"session")
  print(json.dumps(response.json(), indent=4, sort_keys=True))

# print(vars(args))
# print(args)
# sys.exit()

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

# for each record
for i in range(0,len(csv_dict)):
  
  try:
    row = csv_dict[i]
    metadata = liq_meta.render(**row)
    metadata = metadata.replace("{_","{{")
    metadata = metadata.replace("_}","}}")

    local_filename = liq_local.render(**row)
    remote_filename = liq_remote.render(**row)
    
    print("Line",str(i+2)+":",os.path.basename(local_filename), "---->", remote_filename)

    # https://commons.wikimedia.org/w/api.php?action=query&titles=HUA-168481-Portret_van_J.M._ten_Broek,_verkeersleider_bij_de_N.S._in_het_N.S.-station_Amsterdam_C.S._te_Amsterdam.jpg

    if exists(remote_filename):
      print("Upload Error: File Exists",remote_filename)
      continue

    if args.verbose>1:
      print(metadata)

    if args.action=='upload':
      response = upload(local_filename, remote_filename, metadata);
      
      data = response.json()

      if 'error' in data and 'code' in data['error']:
        print("Upload Error",data['error']['code'],data['error']['info'])

        if data['error']['code']=="ratelimited":   #stop trying and wait. else continue to next
          sys.exit()

      elif 'upload' in data and 'result' in data['upload']: 
        print(data['upload']['result'])
        print(data['upload']['imageinfo']['descriptionurl'])

        if 'warnings' in data['upload']:
          print(data['upload']['warnings'])

      else:
        print(json.dumps(data, indent=4, sort_keys=True))

      print()

  except OSError as err:
    print("OS Error: Skipping line",i+2,err)
    pass


