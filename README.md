# NetworkAutomationProject
Our Final CAP Project

# Descriptions
**network_topology file -** The SoC (Source of truth) for this project. This is the file where we will define our network infrastructure. Subnets, routers, and hosts can be added here. The playbook will scan through this file for names, IP, addresses, and such.\
**build_router.j2 -** Jinja template to create routers from the topology file.\
**build_switches.j2 -** Jinja template to create switches from the topology file.\
**build_hosts.j2 -** Jinja template to create hosts from the topology file.\
**set_up_nat.j2 -** Jinja template to establish NAT. These variables are also pulled from the topology file. See these points below for a better understanding of establishing NAT on this virtual network:
  * Create a veth from core to ens3
  * Assign respective IPs
  * Configure NAT within the POSTROUTING iptable chain.
  * Create a summarized route for the network topology.
  * Flush the filter table and nat table.
  * Add an iptables rule to perform NAT for outgoing packets from the respective IP range.
  * Allow forwarding from the ens3 interface (root namespace to the host side of the veth (and vice versa).

# Instructions
- Please ensure python3, pip, and ansible are installed before proceeding. You may find these Ubuntu/Debian commands useful:
  * ```shell
    sudo apt update
    sudo apt install python3
    sudo apt install python3-pip
    sudo apt install ansible
- cd into whichever directory you would like to download the project into.
- ```shell
  git clone https://github.com/DiospyrosD/NetworkAutomationProject.git
- ```shell
  cd NetworkAutomationProject
- To create the network. If issues occur or the playbook is interrupted, run the 'destroy' playbook before re-installing.
  * ```shell
    ansible-playbook create_network.yml
  * ```shell
    ansible-playbook destroy_network.yml # to remove the network from your machine.

- run `sudo python3 vm_deploy.py` to create a VM. The current program allows for 1 VM to be created pulling interface names/IP addresses from the network_topology.yml.
  * You may be prompted to select `enter` for "OK" to acknowledge that a newer version of the kernel is available.
  * The default login is `root` with a password of `alta3`.
- run `python3 wg.py` (no sudo) to launch a script that connects wireguard to three hosts (i.e., charlie, bravo, and bchd). This script is meant for a custom environment built by alta3.
  * You may destroy your wireguard environment by executing `bash wg_destroy.sh`
