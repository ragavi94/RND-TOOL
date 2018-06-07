#!/usr/bin/python

from math import *
import subprocess
import os
import pexpect

with open('./scripts/connectivitymat.txt') as f:
  connectivity_mat = f.read()

## Reading the node names
connectivity_mat_row = connectivity_mat.strip().split("\n")
nodes = connectivity_mat_row[0].strip().split()
node_num = len(nodes)

## Getting the PIDs of nodes
pids=['pids']
for i in range(0,node_num):
  output = subprocess.Popen("sudo docker inspect -f '{{.State.Pid}}' "+nodes[i], stdout=subprocess.PIPE, shell=True)
  (out, err) = output.communicate()
  pids.append(out.strip())
##

open('./connectivity_map.txt', 'w').close() #Clear Previous data
file =open('./connectivity_map.txt','a')
file.write("Connections:\n")

class vethports:
    current_octet=1
    base_ip=1
    def __init__(self,portname1,portname2):

        self.port1=portname1
        self.port2=portname2
        self.port1ip="192.168."+str(vethports.current_octet)+"."+str(vethports.base_ip)+"/24"
        self.port2ip="192.168."+str(vethports.current_octet)+"."+str(vethports.base_ip+1)+"/24"
        vethports.current_octet+=1

for i in range(1,(node_num+1)):
        current_node = connectivity_mat_row[i].strip().split()

        for j in range(i,(node_num+1)):
                if current_node[j] !="0":
##THIS CREATES A LIST WITH OBJECTS OF CLASS vethports (EACH OBJECT IS ONE VETH PAIR) AND INITIALIZES THE OBJECTS WITH PORT NAMES AND IPS  
#INCREMENT OF IP OCTET IS HANDLED BY CLASS VARIABLE current_octet WHENEVER A NEW OBJECT IS CREATED                  
                    vethlist=[]
                    for x in range(1,int(current_node[j])+1):
                        portname1="eth"+str(j)+str(x)
                        portname2="eth"+str(i)+str(x)
                        vethlist.append(vethports(portname1,portname2))

                        
##THIS WILL ADD EACH OBJECT TO THE RESPECTIVE NAMESPACES AND WRITE THE OUTPUT TO connectivity_map.txt                       
                    for vethobj in vethlist:
                        os.system("sudo ip link add vport1 type veth peer name vport2")
                        os.system("sudo ip link set dev vport1 netns "+pids[i]+" name "+vethobj.port1+" up")
                        os.system("sudo ip link set dev vport2 netns "+pids[j]+" name "+vethobj.port2+" up")
                        os.system("sudo docker exec "+nodes[i-1]+" ip addr add "+vethobj.port1ip+" dev "+vethobj.port1)
                        os.system("sudo docker exec "+nodes[j-1]+" ip addr add "+vethobj.port2ip+" dev "+vethobj.port2)
                        file.write(nodes[i-1] +" "+ vethobj.port1 + " ("+vethobj.port1ip+") --- "+nodes[j-1]+" "+ vethobj.port2+ " ("+vethobj.port2ip+")\n")


file.close()
## Start Quagga and ssh process and set ssh password on all Containers
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


