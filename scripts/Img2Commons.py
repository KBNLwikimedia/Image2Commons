#!/usr/local/bin/python3
import json
import sys
from CommonsUpload import upload
import pandas
from liquid import Liquid

if len(sys.argv)<5:
  print('Usage: '+__file__+' CSV_FILE META_TEMPLATE_FILE LOCAL_IMAGE_TEMPLATE REMOTE_IMAGE_TEMPLATE')
  sys.exit(1)

# meta_template_text = open(sys.argv[2], "r").read()

csv_df = pandas.read_csv(sys.argv[1])
csv_df.fillna("", inplace=True) #fill empty cells with ""

csv_dict=csv_df.to_dict(orient='records')

liq_meta = Liquid(sys.argv[2], liquid_from_file=True) 
liq_local = Liquid(sys.argv[3], liquid_from_file=True) 
liq_remote = Liquid(sys.argv[4], liquid_from_file=True) 

for i in range(0,len(csv_dict)):
  row = csv_dict[i]
  metadata = liq_meta.render(**row)
  metadata = metadata.replace("{_","{{")
  metadata = metadata.replace("_}","}}")

  local_filename = liq_local.render(**row)
  remote_filename = liq_remote.render(**row)
  
  print(local_filename, "---->", remote_filename)
  print(metadata)

  response = upload(local_filename, remote_filename, metadata);
  print(json.dumps(response.json(), indent=4, sort_keys=True))


