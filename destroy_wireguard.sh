#!/bin/bash
set -euox pipefail

# Uninstall
pushd ~/wg
rm -rf conf j2 keys

ssh-keyscan -t rsa bravo   >> ~/.ssh/known_hosts
ssh-keyscan -t rsa charlie >> ~/.ssh/known_hosts
ssh-keygen -H
rm ~/.ssh/known_hosts.old

sudo ip link del dev wg0 type wireguard
ssh bravo   sudo ip link del dev wg0 type wireguard
ssh charlie sudo ip link del dev wg0 type wireguard
ssh charlie sudo ip netns delete warp
ssh bravo sudo ip netns delete warp
sudo ip netns delete warp

sudo rm /etc/wireguard/wg0.conf
ssh bravo   sudo rm /etc/wireguard/wg0.conf
ssh charlie sudo rm /etc/wireguard/wg0.conf
popd
