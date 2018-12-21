#!/usr/bin/python

from math import *
import subprocess
import os
import pexpect
import sys  
sys.path.append("./scripts/")
from json_utils import json_util

device = []
link = []
json_obj = json_util()
device, link, link_map = json_obj.read_input_json()

node_num = len(device)
veth_pairs_list = []
device_intfs_list = []
device_ip_list = []
device_status_list = []


## Getting the PIDs of nodes
pids=['pids']
for i in range(0,node_num):
  output = subprocess.Popen("sudo docker inspect -f '{{.State.Pid}}' "+device[i]['device_name'], stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  pids.append(out.strip())
##

## Getting IP Addresses of Nodes
ipaddr_list = ['ips']
for i in range(0,node_num):
  output = subprocess.Popen("sudo docker inspect -f '{{ .NetworkSettings.IPAddress }}' "+device[i]['device_name'], stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  ipaddr_list.append(out.strip())

##



open('/var/lib/rnd_lab/topology_conf.json', 'w').close() #Clear Previous data


class vethports:
    current_octet=1
    base_ip=1
    subnet="192.168."
    mask="/24"
    def __init__(self,portname1,portname2):

        self.port1=portname1
        self.port2=portname2
        self.port1ip=vethports.subnet+str(vethports.current_octet)+"."+str(vethports.base_ip)+vethports.mask
        self.port2ip=vethports.subnet+str(vethports.current_octet)+"."+str(vethports.base_ip+1)+vethports.mask
        vethports.current_octet+=1
#**************YANGS INTERFACE PARAMETERS************************     
#        name = None        
#        type = None                             
#        description = None                       
#        admin-status = None                      
#        oper-status = None                     
#        last-change = None                      
#        if-index = None                      
#        link-up-down-trap-enable = None         
#        phys-address = None                     
#        higher-layer-if and lower-layer-if = None
#        speed = None                             
#        discontinuity-time = None                
#        in-octets = None                        
#        in-unicast-pkts = None                  
#        in-broadcast-pkts = None                 
#        in-multicast-pkts = None                
#        in-discards = None                       
#        in-errors = None                        
#        in-unknown-protos = None                 
#        out-octets = None                       
#        out-unicast-pkts = None                  
#        out-broadcast-pkts = None                
#        out-multicast-pkts = None               
#        out-discards = None                      
#        out-errors = None


for key in sorted(link_map.iterkeys()):
##THIS CREATES A LIST WITH OBJECTS OF CLASS vethports (EACH OBJECT IS ONE VETH PAIR) AND INITIALIZES THE OBJECTS WITH PORT NAMES AND IPS
        print key
        intf = key.split('-')
        intf1 = intf[0]
        intf2 = intf[1]
        vethlist=[]
        for x in range(1,link_map[key]+1):
          portname1 = "eth"+intf2[-1]+str(x)  ## list[-1] to access the last char ie) device number
          portname2 = "eth"+intf1[-1]+str(x)
          vethlist.append(vethports(portname1,portname2))
        veth_pairs_list.append(vethlist)
##THIS WILL ADD EACH OBJECT TO THE RESPECTIVE NAMESPACES AND WRITE THE OUTPUT TO connectivity_map.txt
        for vethobj in vethlist:
          output = subprocess.Popen("sudo ip link add vport1 type veth peer name vport2", stdout=subprocess.PIPE, shell=True)
          (out, err) = output.communicate()
          output = subprocess.Popen("sudo ip link set dev vport1 netns "+pids[int(intf1[-1])]+" name "+vethobj.port1+" up", stdout=subprocess.PIPE, shell=True)
          (out, err) = output.communicate()
          output = subprocess.Popen("sudo ip link set dev vport2 netns "+pids[int(intf2[-1])]+" name "+vethobj.port2+" up", stdout=subprocess.PIPE, shell=True)
          (out, err) = output.communicate()
          output = subprocess.Popen("sudo docker exec "+intf1+" ip addr add "+vethobj.port1ip+" dev "+vethobj.port1, stdout=subprocess.PIPE, shell=True)
          (out, err) = output.communicate()
          output = subprocess.Popen("sudo docker exec "+intf2+" ip addr add "+vethobj.port2ip+" dev "+vethobj.port2, stdout=subprocess.PIPE, shell=True)
          (out, err) = output.communicate()
          

## This block uses docker commands to get ipaddr,management ips, status of the device etc from the created live topology. These data are sent as lists to the json_utils file to form json
for i in range(1,len(device)+1):
	device_ip = []
        device_intfs = (subprocess.Popen(" sudo docker exec "+ device[i-1]['device_name'] + " ip -o link show | awk -F': ' '{print $2}' ", stdout=subprocess.PIPE, shell=True)).communicate()[0].split('\n')
	device_intfs_list.append(device_intfs)
	for intf in range(0,len(device_intfs)-1):
		device_ip.append((subprocess.Popen(" sudo docker exec "+ device[i-1]['device_name'] +" ip -f inet addr show "+ device_intfs[intf].split('@')[0] +" $1 | grep -Po 'inet \K[\d.]+' ", stdout=subprocess.PIPE, shell=True)).communicate()[0].split('\n'))
	device_ip_list.append(device_ip)
	device_status = (subprocess.Popen(" sudo docker inspect -f '{{.State.Status}}' "+device[i-1]['device_name'], stdout=subprocess.PIPE, shell=True)).communicate()
	device_status_list.append(device_status[0].strip())
	                    
        
#Start Quagga and ssh process and set ssh password on all Containers
for i in range(0,len(device)):
        os.system("sudo docker exec "+device[i]['device_name']+" /etc/init.d/quagga start")
        os.system("sudo docker exec "+device[i]['device_name']+" /etc/init.d/ssh start")
        child =pexpect.spawn("sudo docker exec -i -t "+device[i]['device_name']+" passwd root")
        child.expect('Enter new UNIX password:')
        child.sendline('root')
        child.expect('Retype new UNIX password:')
        child.sendline('root')
        child.expect('passwd: password updated successfully')
        child.expect('\n')


json_obj.write_output_json(link_map,ipaddr_list,veth_pairs_list,device_intfs_list,device_ip_list,device_status_list)




