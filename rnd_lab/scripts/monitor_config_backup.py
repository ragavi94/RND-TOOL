#!/usr/bin/python

from time import sleep
from os import listdir
from datetime import datetime
import json


sleeptime = 10

 
def compare(curr_json,new_json,file):
       
        
        if(type(curr_json) is list): 
            if (type(new_json) != list):
                return False
            if (len(curr_json) != len(new_json)): ##find if something has been added or deleted
                if len(curr_json) > len(new_json):
                    file.write("json block deleted")
                    changed = [x for x in curr_json if x not in new_json]
                else:
                    file.write("json block added")
                    changed = [x for x in new_json if x not in curr_json]
                for item in changed:
                    json.dump(item, file, indent=4)
            else:
                for list_index,list_item in enumerate(curr_json):
                    if (not compare(list_item,new_json[list_index],file)): ##recursive call with values of the list
                        if (not ("device" in new_json[list_index] and "link" in new_json[list_index])):
                            json.dump(new_json[list_index], file, indent=4)
                            file.write("\n\n\n")
                        
            return True
		
        if(type(curr_json) is dict):
            if type(new_json) != dict:
                return False
            for key,value in curr_json.items():
                if (type(value) == list and value != new_json[key]): ##print the parent key entry of a block eg: topology,device,link 
                    file.write(key+"\n")
                if (not compare(value,new_json[key],file)): ##recursive calls with values of the dictionary
                    if type(new_json[key]) != list:
                        file.write("changed data::"+key+":"+new_json[key]+"\n")
                    return False
           
            return True

        return ((curr_json == new_json) and (type(curr_json) is type(new_json)))
        



##read previous and updated json data to check for changes

if ".old_topology.json" in listdir("/etc/rnd_lab/"):
    with open("/etc/rnd_lab/.old_topology.json","r") as f:
         curr_json = json.load(f)

else:
    with open("/etc/rnd_lab/topology_config.json", "r") as f:
         curr_json = json.load(f)

while True:
    file = open("/etc/rnd_lab/update_topology_info.txt","a+")
    with open("/etc/rnd_lab/topology_config.json", "r") as f:
         new_json = json.load(f)
         if new_json != curr_json:
             file.write(str(datetime.now())+"\n")
             compare(curr_json,new_json,file)
         curr_json = new_json  ##replacing the new_json as curr_json for update check the next time
    with open("/etc/rnd_lab/.old_topology.json","w") as f:
         json.dump(curr_json, f, indent=4)
    f.close()
    file.close()
    sleep(sleeptime)
    
