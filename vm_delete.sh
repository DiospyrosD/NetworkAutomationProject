#!/bin/bash

sudo pkill qemu-system
pushd /var/kvm/images > /dev/null
sudo rm -rf meta-data* && sudo rm -rf user-data* && sudo rm -rf *.iso && sudo rm -rf *.img && sudo rm -rf net-config*
cd /var/log/qemu
sudo rm -rf ./*serial.log && sudo rm -rf *qemu.log
popd > /dev/null
sudo rm -rf bionic*
sudo ip link del dev br0
echo "The VM and related files have been removed"
