#!/bin/bash

# Get the local IP address
HOST_IP=$(ip a | grep -o 'inet 10\.[0-9]\+\.[0-9]\+\.[0-9]\+' | awk '{print $2}' | head -n 1)

# Run the SSH command to retrieve data from alpha. Remember we are targeting our local machine BCHD on port 5555.
SSH_OUTPUT=$(sudo -u student ssh student@alpha "curl $HOST_IP:5555")

# Echo the output to everyone ssh'd into the machine
echo "Output from alpha: $SSH_OUTPUT" | wall
echo "Remember, I'm SSH'ing into alpha and targetting bchd host (IP: $HOST_IP)" | wall
