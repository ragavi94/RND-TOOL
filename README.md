# RND-TOOL

[![EB2-2027](https://img.shields.io/badge/EB2__2027-Since__2015-green.svg)](https://sites.google.com/a/ncsu.edu/summer15eb22027/)
[![Latest Version](https://img.shields.io/badge/LatestVersion-v1.0-yellow.svg)](https://github.ncsu.edu/EB2-2027/RND-TOOL/releases/tag/v1.0)


## Table of Contents
* [Running the RND Tool](#running-the-rnd-tool)
* [Getting Packet Captures](#packet-capture)
* [Contributing](#contributing)

## Running the RND Tool:
1. If the customized ubuntu image is not built in the host before, build it by running the playbook, `create_quagga_image.yml`:

   `sudo ansible-playbook create_quagga_image.yml -i inventory --extra-vars="ansible_sudo\pass=<sudo password>`
   
2. Modify the network adjacency matrix (`./scripts/connectivitymat.txt`) according to the required topology. Information of the connectivity matrix is in `./readme/connectivity.txt`
3. Run the `connectivity_script.yml` playbook to create the topology:

   `sudo ansible-playbook connectivity_script.yml -i inventory`

4. Management IP addresses of the containers are assigned in the range 172.17.0.2 -172.17.0.254, sequencially and by the order in which they are placed in the network connectivity matrix. 
5. To access a container: do ssh to the management IP with username: `root` password: `root`.
6. Once inside a router, to enter in the router CLI, type `vtysh` and hit enter.


## Packet Capture:

In the directory where the file `collect_capture.py` is saved.
Run command:
`python collect_capture.py` with four command line arguments.

where arguments are:
* `interface`= The interface on which you want to capture trace.
* `exec_time`= For how long you want to capture.
* `host_user`= Username of your host machine on which you want to save the capture.
* `dest_directory`= The path on you machine where you want to save the capture.

For example:

`python collect_capture.py eth1 10 vm1 /home/vm1/trace`

where: 
  * `eth1` indicates the interface on which we want to capture the trace. 
  *  10` indicated the time for which we want to capture the trace.
  * `vm1` indicates the username of the host machine provided  by the Professor. 
  * `/home/vm1/trace` indicates the directory on my machine where we want to save my capture.
  
  After running this command you will be prompted to enter the host password for two times.
  After completion of command you will find pcap file in the host machine in the directory you specified. 
  The file will be saved in the format:
  
  `filename=myhost+"_"+interface+"_"+timestamp+".pcap"`

## Contributing

1. Fork the repo.
2. [Follow the coding practice guideline](#coding-practice-guidelines)
2. Create your own branch (`git checkout -b my-branch`)
3. Commit your changes in the branch (`git commit -am "My Changes"`)
4. Push your branch (`git push origin my-branch`)
5. Send a pull request

## Coding Practice Guidelines
1. Commit Small Commit Often
2. Always comment the code.
3. Use Macros instead of hardcoded values.
