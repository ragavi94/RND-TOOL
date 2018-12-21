#!/usr/bin/python

from math import *
from datetime import datetime
import subprocess
import os
import pexpect
import json
from collections import OrderedDict


with open('./scripts/connectivitymat.txt') as f:
  connectivity_mat = f.read()

## Reading the node names/var/rnd_lab/topology_conf.json
connectivity_mat_row = connectivity_mat.strip().split("\n")
nodes = connectivity_mat_row[0].strip().split()
node_num = len(nodes)
device_id = 1000
## Dictionary for the json file in /var/lib/rnd_lab/topology_conf.json
topology_data = {}
device_data = {}
link_data = {}
interface_data = {}
device_data['device'] = []
link_data['link'] = []
interface_data['interface'] = []

## Getting the PIDs of nodes
pids=['pids']
for i in range(0,node_num):
  output = subprocess.Popen("sudo docker inspect -f '{{.State.Pid}}' "+nodes[i], stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  pids.append(out.strip())
##

## Getting IP Addresses of Nodes
ipaddr_list = ['ips']
for i in range(0,node_num):
  output = subprocess.Popen("sudo docker inspect -f '{{ .NetworkSettings.IPAddress }}' "+nodes[i], stdout=subprocess.PIPE, shell=True)
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

for i in range(1,(node_num+1)):
        current_node = connectivity_mat_row[i].strip().split()
	device_id += 1
        for j in range(i,(node_num+1)):
                if current_node[j] !="0":
##THIS CREATES A LIST WITH OBJECTS OF CLASS vethports (EACH OBJECT IS ONE VETH PAIR) AND INITIALIZES THE OBJECTS WITH PORT NAMES AND IPS                    
                    vethlist=[]
                    for x in range(1,int(current_node[j])+1):
                        portname1="eth"+str(j)+str(x)
                        portname2="eth"+str(i)+str(x)
                        vethlist.append(vethports(portname1,portname2))

                        
##THIS WILL ADD EACH OBJECT TO THE RESPECTIVE NAMESPACES AND WRITE THE OUTPUT TO connectivity_map.txt                       
                    for vethobj in vethlist:
                        output = subprocess.Popen("sudo ip link add vport1 type veth peer name vport2", stdout=subprocess.PIPE, shell=True)
                        (out, err) = output.communicate()
                        output = subprocess.Popen("sudo ip link set dev vport1 netns "+pids[i]+" name "+vethobj.port1+" up", stdout=subprocess.PIPE, shell=True)
                        (out, err) = output.communicate()
                        output = subprocess.Popen("sudo ip link set dev vport2 netns "+pids[j]+" name "+vethobj.port2+" up", stdout=subprocess.PIPE, shell=True)
                        (out, err) = output.communicate()
                        output = subprocess.Popen("sudo docker exec "+nodes[i-1]+" ip addr add "+vethobj.port1ip+" dev "+vethobj.port1, stdout=subprocess.PIPE, shell=True)
                        (out, err) = output.communicate()
                        output = subprocess.Popen("sudo docker exec "+nodes[j-1]+" ip addr add "+vethobj.port2ip+" dev "+vethobj.port2, stdout=subprocess.PIPE, shell=True)
                        (out, err) = output.communicate()
                        #file.write(nodes[i-1] +" "+ vethobj.port1 + " ("+vethobj.port1ip+") --- "+nodes[j-1]+" "+ vethobj.port2+ " ("+vethobj.port2ip+")\n")
			link_data['link'].append({ 'link_id': '12345' , 'link_type': 'test' , 'metric': 'test' ,'source_node': nodes[i-1] , 'source_intf': vethobj.port1 , 'source_intf_ip': vethobj.port1ip , 'dest_node': nodes[j-1] , 'dest_intf': vethobj.port2 , 'dest_intf_ip': vethobj.port2ip})

	device_intfs = (subprocess.Popen(" sudo docker exec "+ current_node[0]  + " ip -o link show | awk -F': ' '{print $2}' ", stdout=subprocess.PIPE, shell=True)).communicate()[0].split('\n')
	interface_data['interface'] = []
	for intf in range(0,len(device_intfs)-1):
		device_ip = (subprocess.Popen(" sudo docker exec "+ current_node[0] +" ip -f inet addr show "+ device_intfs[intf].split('@')[0] +" $1 | grep -Po 'inet \K[\d.]+' ", stdout=subprocess.PIPE, shell=True)).communicate()[0]
		interface_data['interface'].append({ 'interface_uid': 'test' , 'interface_type': 'abc' , 'interface_name': device_intfs[intf].split('@')[0] , 'interface_ip': device_ip })
	device_status = (subprocess.Popen(" sudo docker inspect -f '{{.State.Status}}' "+current_node[0], stdout=subprocess.PIPE, shell=True)).communicate()
	                    
        device_data['device'].append({ 'device_name': current_node[0] , 'device_id': device_id , 'device_image': 'quagga' , 'gateway': '172.17.0.1' , 'ipaddress': ipaddr_list[i] , 'status': device_status[0].strip() , 'username': 'root' , 'password': 'root' ,'interface': interface_data['interface']})

#Start Quagga and ssh process and set ssh password on all Containers
for i in nodes:
        os.system("sudo docker exec "+i+" /etc/init.d/quagga start")
        os.system("sudo docker exec "+i+" /etc/init.d/ssh start")
        child =pexpect.spawn("sudo docker exec -i -t "+i+" passwd root")
        child.expect('Enter new UNIX password:')
        child.sendline('root')
        child.expect('Retype new UNIX password:')
        child.sendline('root')
        child.expect('passwd: password updated successfully')
        child.expect('\n')

topology_data['topology'] = []
topology_data['topology'].append({
    'topology_id': '101',
    'topology_type': 'test',
    'create_time': str(datetime.now()),
    'modified_time': str(datetime.now()),
    'device': device_data['device'],
    'link': link_data['link']
})

with open('/var/lib/rnd_lab/topology_conf.json', 'a') as outfile:
    json.dump(OrderedDict(topology_data), outfile, indent=4, sort_keys=False)




