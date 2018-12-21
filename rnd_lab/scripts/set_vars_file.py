#!/usr/bin/python

import sys
sys.path.append("./scripts/")
from json_utils import json_util

device = []
link = []
node_list = []
json_obj = json_util()
device, link, link_map = json_obj.read_input_json()

for i in range(0,len(device)):
   node_list.append(device[i]['device_name'])

node_num = len(node_list)

open('./scripts/vars_file.yaml', 'w').close() #Clear Previous data
file =open('./scripts/vars_file.yaml','a')
file.write("container_names:\n")
for node_name in node_list:
  file.write("  - "+node_name+"\n")

