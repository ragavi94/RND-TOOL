Execution:
1. If the customized ubuntu image is not built in the host before, build it by running the playbook, create_quagga_image.yml 
   sudo ansible-playbook create_quagga_image.yml -i inventory --extra-vars="ansible_sudo\pass=<sudo password>"
2. Modify the network topology json present under  (/etc/rnd_lab/topology_config.json) according to the required topology. Information about the input json is present under input_readme.txt
3. Run the connectivity_script.yml playbook to create the topology.
   sudo ansible-playbook connectivity_script.yml -i inventory"
4. Management IP addresses of the containers are assigned in the range 172.17.0.2 -172.17.0.254, sequencially and by the order in which they are placed in the network connectivity matrix. 
5. On successful creation of the topology, a json that consists the live configuration and status of the devices/links can be found under (/var/lib/rnd_lab/topology_conf.json).
6. To access a container: do ssh to the management IP with username: root password: root
7. Once inside a router, to enter in the router CLI, type vtysh and hit enter.


 
