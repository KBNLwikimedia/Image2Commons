#!/usr/local/bin/python3
import json
import sys
from CommonsUpload import upload
import pandas
from liquid import Liquid
import argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Uploads images in batch to Wikimedia Commons')
  parser.add_argument('--csv',help="input csv file", required=True)
  parser.add_argument('--metadata',help="metadata template", required=True)
  parser.add_argument('--local-image',help="local image template", required=True)
  parser.add_argument('--remote-image',help="remote image template", required=True)
  parser.add_argument('action', choices=['test', 'upload'])
  parser.add_argument('--verbose', '-v', action='count', default=0)
  args = parser.parse_args()

# read csv
csv_df = pandas.read_csv(args.csv)
csv_df.fillna("", inplace=True) #fill empty cells with ""
csv_dict=csv_df.to_dict(orient='records')

# read templates
liq_meta = Liquid(args.metadata, liquid_from_file=True) 
liq_local = Liquid(args.local_image, liquid_from_file=True) 
liq_remote = Liquid(args.remote_image, liquid_from_file=True) 

# for each record
for i in range(0,len(csv_dict)):
  row = csv_dict[i]
  metadata = liq_meta.render(**row)
  metadata = metadata.replace("{_","{{")
  metadata = metadata.replace("_}","}}")

  local_filename = liq_local.render(**row)
  remote_filename = liq_remote.render(**row)
  
  print(local_filename, "---->", remote_filename)

  if args.verbose>1:
    print(metadata)

  if args.action=='upload':
    response = upload(local_filename, remote_filename, metadata);
    # if args.verbose>1 or response.status_code!=200: -->> status_code altijd 200 ook bij error
    print(json.dumps(response.json(), indent=4, sort_keys=True))
    # else:
    # print("ok")


