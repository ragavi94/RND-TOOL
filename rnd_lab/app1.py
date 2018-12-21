#!flask/bin/python
from flask import Flask, request
import json
import os
import subprocess


app = Flask(__name__)


with open('/etc/rnd_lab/topology_config.json') as fd:
      config_json = json.load(fd)
running_config = config_json['topology'][0]
fd.close()

topology_data = {}
topology_data['topology'] = []

def update_utility(running_config):
    if len(topology_data['topology']) == 0:
        topology_data['topology'].append(running_config) 
    else:
        topology_data['topology'][0] = running_config  ##needs to be changed to support multiple topologies
        file = open("/etc/rnd_lab/topology_config.json","w")
        json.dump(topology_data,file,indent=4)
        file.close()


@app.route('/topology_live_config', methods=['GET'])
def get_topology(): # get the entire running configuration as seen in the /var/lib folder 
    return json.dumps({'topology': running_config},indent=4),201

@app.route('/search_topology', methods=['POST'])
def search_topology(): #search for a device/device interface/links between two devices
    i=0
    if not request.json:
        abort(400)
    request_json = request.json
    if request_json['device_name'] and request_json['interface_name'] != "": #device interface search
        for i in range(0,len(running_config['device'])):
           if running_config['device'][i]['device_name'] == request_json['device_name']:
               for j in range(0,len(running_config['device'][i]['interface'])):
                     if running_config['device'][i]['interface'][j]['interface_name'] == request_json['interface_name']:
                         intf_data = running_config['device'][i]['interface'][j]
                         return json.dumps({'interface': intf_data},indent=4),201

    if request.json['device_name'] != None:
        for i in range(0,len(running_config['device'])): #device search
           if running_config['device'][i]['device_name'] == request_json['device_name']:
               device_data = running_config['device'][i]
               return json.dumps({'device': device_data},indent=4),201
 
    if 'link' in request.json: #search for link between two devices by either giving only src or both src and dest
        link_data = []
        if request_json['link']['source_node'] and request_json['link']['dest_node'] != "":
           for i in range(0,len(running_config['link'])):
               if (running_config['link'][i]['source_node'] == request_json['link']['source_node']) and (running_config['link'][i]['dest_node'] == request_json['link']['dest_node']):
                     link_data.append(running_config['link'][i])
           if not link_data:
               return json.dumps({'link': "No links found"},indent=4),201
           else:
               return json.dumps({'link': link_data},indent=4),201


        if request_json['link']['source_node'] != None:    
           for i in range(0,len(running_config['link'])):
               if (running_config['link'][i]['source_node'] == request_json['link']['source_node']):
                     link_data.append(running_config['link'][i])
           if not link_data:
               return json.dumps({'link': "No links found"},indent=4),201
           else:
               return json.dumps({'link': link_data},indent=4),201

@app.route('/update_topology/add_device', methods=['PUT'])
def update_topology_add_device(): #add a device in the running config. changes the /etc/update_json file. 

    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0
    if request_json['device'] != "":
        for dev_item in running_config['device']:
            if request_json['device']['device_name'] == dev_item['device_name']:
                flag = 1
        if flag:
            return json.dumps({'topology':"Cannot add. Device already found"},indent=4),200
        else:
            running_config['device'].append(request_json['device']) ##add new device to the exisitng json structure
            update_utility(running_config)           
            return json.dumps({'topology':"Device added in /etc/rnd_lab/topology_config.json"},indent=4),201

@app.route('/update_topology/add_interface', methods=['PUT'])
def update_topology_add_intf():
    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0
    device_index = 0    
    if request_json['device']['interface'] != "":
        for dev_item in running_config['device']:
            if request_json['device']['device_name'] == dev_item['device_name']:
                device_index = running_config['device'].index(dev_item)
            for intf_item in dev_item['interface']:
                if request_json['device']['interface']['interface_name'] == intf_item['interface_name']:
                    flag = 1
        if flag:
            return json.dumps({'topology':"Cannot add. Device interface already found"},indent=4),200    
        else:
            dev_item['interface'].append(request_json['device']['interface']) 
            running_config['device'][device_index]['interface'] = dev_item['interface']  ##add new device interface to the exisitng json structure
            update_utility(running_config)
            return json.dumps({'topology':"Interface added in /etc/rnd_lab/topology_config.json"+str(device_index)},indent=4),201
   
@app.route('/update_topology/add_link', methods=['PUT']) 
def update_topology_add_link():
    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0
    if request_json['link'] != "":
        for link_item in running_config['link']:
            if (request_json['link']['source_node'] == link_item['source_node']) and (request_json['link']['dest_node'] == link_item['dest_node']) and (request_json['link']['source_intf'] == link_item['source_intf']) and (request_json['link']['dest_intf'] == link_item['dest_intf']):
                flag = 1
        if flag:
       	    return json.dumps({'topology':"Cannot add. Link already found"},indent=4),200
	else:
	    running_config['link'].append(request_json['link']) ##add new link to the existing json structure
            update_utility(running_config)
	    return json.dumps({'topology':"Link added in /etc/rnd_lab/topology_config.json"},indent=4),201         

@app.route('/update_topology/del_device', methods=['PUT'])
def update_topology_del_device(): #delete a device in the running config. changes the /etc/update_json file. 

    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0
    if request_json['device'] != "":
        for dev_item in running_config['device']:
            if request_json['device']['device_name'] == dev_item['device_name']:
                flag = 1
        if not flag:
            return json.dumps({'topology':"Cannot delete. Device is not present"},indent=4),200
        else:
            running_config['device'].remove(request_json['device']) ##delete device from the existing json structure
            update_utility(running_config)
            return json.dumps({'topology':"Device deleted in /etc/rnd_lab/topology_config.json"},indent=4),201

@app.route('/update_topology/del_interface', methods=['PUT'])
def update_topology_del_intf():
    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0
    device_index = 0
    if request_json['device']['interface'] != "":
        for dev_item in running_config['device']:
            for intf_item in dev_item['interface']: 
                if request_json['device']['interface']['interface_name'] == intf_item['interface_name']:
                    device_index = running_config['device'].index(dev_item)
                    flag = 1
            if not flag:
                return json.dumps({'topology':"Cannot delete. Device interface not present"},indent=4),200
            else:
                dev_item['interface'].remove(request_json['device']['interface']) ##delete device interface from the exisitng json structure
                running_config['device'][device_index]['interface'] = dev_item['interface']
                update_utility(running_config)
                return json.dumps({'topology':"Device Interface deleted in /etc/rnd_lab/topology_config.json"},indent=4),201

@app.route('/update_topology/del_link', methods=['PUT'])
def update_topology_del_link():
    if not request.json:
        abort(400)
    request_json = request.json
    flag = 0            
    if request_json['link'] != "":
        for link_item in running_config['link']:
            if (request_json['link']['source_node'] == link_item['source_node']) and (request_json['link']['dest_node'] == link_item['dest_node']) and (request_json['link']['source_intf'] == link_item['source_intf']) and (request_json['link']['dest_intf'] == link_item['dest_intf']):
                flag = 1
        if not flag:
            return json.dumps({'topology':"Cannot delete. Link is not present"},indent=4),200
        else:
            running_config['link'].remove(request_json['link'])  ##delete link from the existing json structure
            update_utility(running_config)
            return json.dumps({'topology':"Value Updated in /etc/rnd_lab/topology_config.json"},indent=4),201
			
if __name__ == '__main__':
    app.run(port=7000)
