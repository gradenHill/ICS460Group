#!/bin/bash

# Fix permissions for the current user
sudo chown -R $SUDO_USER:$SUDO_USER .

# Default answers to the package manager, prevent user from needing to answer them.
export DEBIAN_FRONTEND=noninteractive

# download latest list of available software (-qq = quietly)
sudo apt-get update -qq

# Pipe in answers to Wireshark questions. Allows non-root users to save network packets.
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections

# install everything needed to run the lab (-qq = quietly, -y == automatically)
sudo apt-get install -y -qq snort tcpdump wireshark python3 python3-pip python3-scapy tmux

# Delete namespaces if they already exist
# `2>/dev/null` silences expected errors
sudo ip netns del attacker 2>/dev/null
sudo ip netns del target 2>/dev/null

# recreate the namespacces
sudo ip netns add attacker
sudo ip netns add target

# create the virtual ethernet cable with two named ends
sudo ip link add veth-attack type veth peer name veth-target

# virtually plug the cable into the namespaces
sudo ip link set veth-attack netns attacker
sudo ip link set veth-target netns target

# Assign the namespace ip addresses, and tell them to access the network through the cable
sudo ip netns exec attacker ip addr add 10.0.0.20/24 dev veth-attack
sudo ip netns exec target ip addr add 10.0.0.10/24 dev veth-target

# Go in the attacker namespace and set the links to "on"
sudo ip netns exec attacker ip link set veth-attack up
sudo ip netns exec attacker ip link set lo up

# Go in the target namespace and set the links to "on"
sudo ip netns exec target ip link set veth-target up
sudo ip netns exec target ip link set lo up

# kill any existing tmux NIDS sessions and start new
tmux kill-session -t NIDS 2>/dev/null
tmux new-session -d -s NIDS
    
# TOP PANE: host space
tmux send-keys -t NIDS:0 "clear && printf '=== MANAGEMENT PANE ===\\n\\n' && printf 'To reset the lab, run:\\n\\033[1;31msudo ./setup.sh\\033[0m\\n' && echo" C-m

# create bottom section
tmux split-window -v -t NIDS:0

# LEFT PANE: Run command to enter the target namespace
# C-m is "enter"
# -t = allows you to target the tmux pane
tmux send-keys -t NIDS:1 "sudo ip netns exec target bash" C-m
tmux send-keys -t NIDS:1 " history -s 'snort -A console -q -c ./snort.conf -i veth-target -k none'; clear && printf '=== TARGET SPACE (10.0.0.10) ===\\n\\n' && printf 'Press \\033[1;33mUP ARROW\\033[0m to load command, or type it manually:\\n' && printf '\\033[1;32msnort -A console -q -c ./snort.conf -i veth-target -k none\\033[0m\\n' && echo" C-m

# Split the window into two screens
tmux split-window -h -t NIDS:1

# RIGHT PANE: Run command to enter the attacker namespace, and display available scripts
tmux send-keys -t NIDS:2 "sudo ip netns exec attacker bash" C-m
tmux send-keys -t NIDS:2 "cd attack-scripts/ && clear && printf '=== ATTACKER SPACE (10.0.0.20) ===\\n\\nAvailable attack scripts:\\n' && ls -F && printf '\\nRun \\033[1;32mpython3 <scriptName>.py 10.0.0.10\\033[0m to execute attack script\\n' && echo" C-m

# Enable scrolling and clicking
tmux set -g mouse on

# Attach to the split-view session
tmux attach-session -t NIDS
