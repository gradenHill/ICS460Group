#!/bin/bash

# ==============================================================================
# ICS 460 - NIDS Master Environment & Network Builder
# Prepared for: Graden Hill (Server/Snort Lead) 
# Purpose: Automates tool installation and internal network simulation [cite: 6, 14]
# ==============================================================================

echo "===================================================================="
echo " Starting ICS 460 NIDS Laboratory Provisioning..."
echo "===================================================================="

# ------------------------------------------------------------------------------
# PHASE 1: Tooling & Dependencies [cite: 14, 15]
# ------------------------------------------------------------------------------
echo "[*] PHASE 1: Installing Core Security & Automation Tools..."
export DEBIAN_FRONTEND=noninteractive

# Update system repositories
sudo apt-get update -qq

# Pre-configure Wireshark permissions for non-interactive install
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections

# Install Snort (NIDS), tcpdump (Capture), and Python/Scapy (Attacker) [cite: 15, 16]
sudo apt-get install -y -qq snort tcpdump wireshark python3 python3-pip python3-scapy tmux
echo "[+] All required software packages are installed."

# ------------------------------------------------------------------------------
# PHASE 2: Virtual Network Infrastructure 
# ------------------------------------------------------------------------------
echo "[*] PHASE 2: Building Isolated Network Namespaces..."

# Clean up existing namespaces to ensure a fresh state
sudo ip netns del attacker 2>/dev/null
sudo ip netns del target 2>/dev/null

# Create Attacker and Target namespaces [cite: 10]
sudo ip netns add attacker
sudo ip netns add target

# Create the virtual Ethernet cable (veth pair) to simulate the 'wire' [cite: 7]
sudo ip link add veth-att type veth peer name veth-tar

# Plug the cable into each respective namespace
sudo ip link set veth-att netns attacker
sudo ip link set veth-tar netns target

# ------------------------------------------------------------------------------
# PHASE 3: IP Assignment & Interface Activation
# ------------------------------------------------------------------------------
echo "[*] PHASE 3: Assigning Static IPs (Subnet: 10.0.0.0/24)..."

# Assign IP to Attacker (10.0.0.20) and Target (10.0.0.10)
sudo ip netns exec attacker ip addr add 10.0.0.20/24 dev veth-att
sudo ip netns exec target ip addr add 10.0.0.10/24 dev veth-tar

# Bring interfaces and local loopbacks online
sudo ip netns exec attacker ip link set veth-att up
sudo ip netns exec attacker ip link set lo up

sudo ip netns exec target ip link set veth-tar up
sudo ip netns exec target ip link set lo up

echo "[+] Internal network is live. Target: 10.0.0.10 | Attacker: 10.0.0.20"

# ------------------------------------------------------------------------------
# PHASE 4: Connectivity Verification
# ------------------------------------------------------------------------------
echo "[*] PHASE 4: Running Diagnostic Connectivity Check..."

if sudo ip netns exec attacker ping -c 1 10.0.0.10 &> /dev/null
then
    echo "[+] SUCCESS: Internal link verified. Namespaces can communicate."
else
    echo "[-] FAILED: Link offline. Please check network namespace status."
fi

# ------------------------------------------------------------------------------
# PHASE 5: Automated Workspace Launch (tmux) 
# ------------------------------------------------------------------------------
echo "[*] PHASE 5: Launching NIDS Project Workspace..."

# Check if already in tmux to prevent nesting issues
if [ -z "$TMUX" ]; then
    # Create new session named 'NIDS'
    tmux new-session -d -s NIDS -n 'Lab'
    
    # Left Pane: The Target Environment (Graden Hill) 
    tmux send-keys -t NIDS:0.0 "sudo ip netns exec target bash" C-m
    tmux send-keys -t NIDS:0.0 "clear && echo '--- TARGET SPACE (10.0.0.10) ---' && echo 'Role: Snort Management & PCAP Capture'" C-m
    
    # Split the screen vertically
    tmux split-window -h -t NIDS:0.0

    # Enable scrolling and clicking windows independently
    tmux set -g mouse on

    # Right Pane: The Attacker Environment
    tmux send-keys -t NIDS:0.1 "sudo ip netns exec attacker bash" C-m
    tmux send-keys -t NIDS:0.1 "clear && echo '--- ATTACKER SPACE (10.0.0.20) ---' && echo 'Role: Python & Scapy Attack Scripting'" C-m
    
    # Attach to the split-view session
    tmux attach-session -t NIDS
else
    echo "===================================================================="
    echo " [!] Already inside tmux. Setup complete."
    echo " Enter Target:   sudo ip netns exec target bash"
    echo " Enter Attacker: sudo ip netns exec attacker bash"
    echo "===================================================================="
fi
