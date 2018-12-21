#!/bin/bash

sudo apt-get update
sudo apt-get install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt-get update
yes | sudo apt-get install ansible
yes | sudo apt-get install python-pexpect
yes | sudo apt-get install python-pip
sudo pip install --upgrade pip
yes | sudo apt-get install docker.io
sudo pip install docker-py 
unzip rnd_lab.zip 
sudo cp rnd_lab/rnd_lab.bash /usr/bin
sudo ansible-playbook rnd_lab/create_quagga_image.yml
