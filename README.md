# NetworkAutomationProject
Our Final CAP Project

# Descriptions
network_topology file: The SoC (Source of truth) for this project. This is the file where we will define our network infrastructure. Subnets, routers, and hosts can be added here. The playbook will scan through this file for names, IP, addresses, and such.

# Instructions
- cd into whichever directory you would like to download the project into.
- run 'git clone https://github.com/DiospyrosD/NetworkAutomationProject.git'
- run 'cd NetworkAutomationProject'
- run 'ansible-playbook create_network.yml' to create the network. If issues occur or the playbook is interrupted, run the 'destroy' playbook before re-installing.
- run 'ansible-playbook destroy_network.yml' to remove the network from your machine.

- run 'sudo python3 vm_deploy.py' to create a VM. The current program allows for 1 VM to be created pulling interface names/IP addresses from the network_topology.yml. 
