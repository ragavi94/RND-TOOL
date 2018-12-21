#!/bin/bash

sudo ansible-playbook -i inventory $(echo $(find -iname connectivity_script.yml))
