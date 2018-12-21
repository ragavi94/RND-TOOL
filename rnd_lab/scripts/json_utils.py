import json

from datetime import datetime
from collections import OrderedDict


class json_util:

  def __init__(self):
    self.topology_data = {}
    self.device = []
    self.link = []

  def read_input_json(self):
    ## Reading from /etc/rnd_lab/topology_config.json
    
    link_l = []
    link_map = {}
    with open('/etc/rnd_lab/topology_config.json') as f:
      connectivity_json = json.load(f)
    topology = connectivity_json['topology']

    for i in range(0,len(topology)):
      for j in range(0,len(topology[i]['device'])):
        self.device = topology[i]['device'] ## list of all devices in the topology
      for j in range(0,len(topology[i]['link'])):
        self.link = topology[i]['link'] ## list of all links in the topology
    for x in range(0,len(self.link)):
      intf = str(self.link[x]['source_node']) + '-' + str(self.link[x]['dest_node'])
      link_l.append(intf)
    for link in link_l:
      if link in link_map.keys():
        link_map[link] += 1
      else:
        link_map[link] = 1
    f.close()
    return self.device, self.link, link_map


  def write_output_json(self,link_map,ipaddr_list,veth_pairs_list,device_intfs_list,device_ip_list,device_status_list):
    device_id = 1000 ## temproarily starts from 1000. needs change
    ## Dictionary for the json file in /var/lib/rnd_lab/topology_conf.json
    device_data = {}
    link_data = {}
    interface_data = {}
    device_data['device'] = []
    link_data['link'] = []
    index = 0
    for key in sorted(link_map.iterkeys()):
      
      intf = key.split('-')
      intf1 = intf[0] 
      intf2 = intf[1]
      vethlist = veth_pairs_list[index]
      for vethobj in vethlist: ## constructing link object of the json here
        link_data['link'].append({ 'link_id': '12345' , 'link_type': 'test' , 'metric': 'test' ,'source_node': intf1 , 'source_intf': vethobj.port1 , 'source_intf_ip': vethobj.port1ip , 'dest_node': intf2 , 'dest_intf': vethobj.port2 , 'dest_intf_ip': vethobj.port2ip})
      index += 1

    for i in range(0,len(self.device)):
      ## constructing device object of the json here
      interface_data['interface'] = []
      device_id +=1
      device_intfs = device_intfs_list[i]
      device_ip = device_ip_list[i]
      for intf in range(0,len(device_intfs)-1):
        interface_data['interface'].append({ 'interface_uid': 'test' , 'interface_type': 'abc' , 'interface_name': device_intfs[intf].split('@')[0] , 'interface_ip': device_ip[intf][0] })
  
      device_data['device'].append({ 'device_name': self.device[i]['device_name'] , 'device_id': device_id , 'device_image': 'quagga' , 'gateway': '172.17.0.1' , 'ipaddress': ipaddr_list[i+1] , 'status': device_status_list[i] , 'username': 'root' , 'password': 'root' ,'interface': interface_data['interface']})

    ## constructing topology data
    self.topology_data['topology'] = []
    self.topology_data['topology'].append({
      'topology_id': '101',
      'topology_type': 'test',
      'create_time': str(datetime.now()),
      'modified_time': str(datetime.now()),
      'device': device_data['device'],
      'link': link_data['link']
    })


    with open('/var/lib/rnd_lab/topology_conf.json', 'a+') as outfile:
      json.dump(self.topology_data, outfile, indent=4)
    with open('/etc/rnd_lab/topology_config.json', 'w') as outfile:
      json.dump(self.topology_data, outfile, indent=4)
    outfile.close()
    return 0
