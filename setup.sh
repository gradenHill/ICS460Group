#!/bin/bash

# ==========================================
# ICS 460 - NIDS Master Environment Builder
# Architecture-agnostic (ARM64 & x86_64)
# ==========================================

echo "=========================================="
echo " Starting NIDS Laboratory Provisioning..."
echo "=========================================="

# ------------------------------------------
# PHASE 1: Tooling & Dependencies
# ------------------------------------------
echo "[*] PHASE 1: Installing Required Packages..."
export DEBIAN_FRONTEND=noninteractive

# Update repositories silently
sudo apt-get update -qq

# Pre-configure Wireshark to silently accept default security settings
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections

# Install necessary tools
sudo apt-get install -y -qq snort tcpdump wireshark python3 python3-pip python3-scapy
echo "[+] Packages installed successfully."

# ------------------------------------------
# PHASE 2: Virtual Network Infrastructure
# ------------------------------------------
echo "[*] PHASE 2: Building Isolated Network Namespaces..."

# Clean up existing namespaces if the script is run multiple times
sudo ip netns del attacker 2>/dev/null
sudo ip netns del target 2>/dev/null

# Create fresh namespaces
sudo ip netns add attacker
sudo ip netns add target

# Create the virtual Ethernet cable (veth pair)
sudo ip link add veth-att type veth peer name veth-tar

# Plug each end of the cable into its respective namespace
sudo ip link set veth-att netns attacker
sudo ip link set veth-tar netns target

# ------------------------------------------
# PHASE 3: IP Assignment & Activation
# ------------------------------------------
echo "[*] PHASE 3: Assigning IPs and Bringing Network Online..."

# Assign IPs (Attacker: 10.0.0.20, Target: 10.0.0.10)
sudo ip netns exec attacker ip addr add 10.0.0.20/24 dev veth-att
sudo ip netns exec target ip addr add 10.0.0.10/24 dev veth-tar

# Bring up interfaces and loopbacks inside the namespaces
sudo ip netns exec attacker ip link set veth-att up
sudo ip netns exec attacker ip link set lo up

sudo ip netns exec target ip link set veth-tar up
sudo ip netns exec target ip link set lo up

echo "[+] Virtual network (10.0.0.0/24) is online."

# ------------------------------------------
# PHASE 4: Verification
# ------------------------------------------
echo "[*] PHASE 4: Verifying Connectivity..."

# Ping the Target from the Attacker namespace
if sudo ip netns exec attacker ping -c 1 10.0.0.10 &> /dev/null
then
    echo "[+] SUCCESS: Attacker can reach Target (10.0.0.10)."
else
    echo "[-] FAILED: Network connectivity issue detected."
fi

echo "=========================================="
echo " NIDS Laboratory is Ready! "
echo "------------------------------------------"
echo "To enter the Target environment:   sudo ip netns exec target bash"
echo "To enter the Attacker environment: sudo ip netns exec attacker bash"
echo "=========================================="
