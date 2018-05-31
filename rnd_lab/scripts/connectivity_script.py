#!/usr/bin/python

from math import *
import subprocess
import os
import pexpect

with open('./scripts/connectivitymat.txt') as f:
  connectivity_mat = f.read()

current_octet=1
base_ip=1

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

## Creating and Sending the veth links
for i in range(1,(node_num+1)):
        current_node = connectivity_mat_row[i].strip().split()

        for j in range(i,(node_num+1)):
                if current_node[j] == "1":
                        os.system("sudo ip link add vport1 type veth peer name vport2")
                        port1 = "eth"+str(j)
                        port2 = "eth"+str(i)
                        port1_ip = "192.168."+str(current_octet)+"."+str(base_ip)+"/24"
                        port2_ip = "192.168."+str(current_octet)+"."+str(base_ip+1)+"/24"

                        os.system("sudo ip link set dev vport1 netns "+pids[i]+" name "+port1+" up")
                        os.system("sudo ip link set dev vport2 netns "+pids[j]+" name "+port2+" up")
                        os.system("sudo docker exec "+nodes[i-1]+" ip addr add "+port1_ip+" dev "+port1)
                        os.system("sudo docker exec "+nodes[j-1]+" ip addr add "+port2_ip+" dev eth"+str(i))
                        current_octet=current_octet+1

                        file.write(nodes[i-1] +" "+ port1 + " ("+port1_ip+") --- "+nodes[j-1]+" "+ port2+ " ("+port2_ip+")\n")
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


