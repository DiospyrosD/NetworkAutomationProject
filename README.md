# NetworkAutomationProject
Our Final CAP Project

# Descriptions
**network_topology file -** The SoC (Source of truth) for this project. This is the file where we will define our network infrastructure. Subnets, routers, and hosts can be added here. The playbook will scan through this file for names, IP, addresses, and such.\
**build_router.j2 -** Jinja template to create routers from the topology file.\
**build_switches.j2 -** Jinja template to create switches from the topology file.\
**build_hosts.j2 -** Jinja template to create hosts from the topology file.\
**set_up_nat.j2 -** Jinja template to establish NAT.
  * Create a veth from core to ens3
  * Assign respective IPs
  * Configure NAT within the POSTROUTING iptable chain.
  * Create a summarized route for the network topology.
  * Flush the filter table and nat table.
  * Add an iptables rule to perform NAT for outgoing packets from the respective IP range.
  * Allow forwarding from the ens3 interface (root namespace to the host side of the veth (and vice versa).

# Instructions
- cd into whichever directory you would like to download the project into.
- ```shell `git clone https://github.com/DiospyrosD/NetworkAutomationProject.git`
- run `cd NetworkAutomationProject`
- run `ansible-playbook create_network.yml` to create the network. If issues occur or the playbook is interrupted, run the 'destroy' playbook before re-installing.
- run `ansible-playbook destroy_network.yml` to remove the network from your machine.

- run `sudo python3 vm_deploy.py` to create a VM. The current program allows for 1 VM to be created pulling interface names/IP addresses from the network_topology.yml.
  * You may be prompted to select `enter` for "OK" to acknowledge a newer version of the kernel is available.
  * The default login is `root` with a password of `alta3`.
