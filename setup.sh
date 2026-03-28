#!/bin/bash

# ==========================================
# ICS 460 - NIDS Environment Setup Script
# Compatible with both ARM64 (UTM) and x86_64 (VirtualBox/VMware)
# ==========================================

echo "Starting NIDS environment provisioning..."

# Prevent interactive dialog boxes from halting the installation process
export DEBIAN_FRONTEND=noninteractive

echo "[1/4] Updating system package repositories..."
sudo apt-get update && sudo apt-get upgrade -y

echo "[2/4] Installing Core Networking & Capture Tools..."
# Pre-configure Wireshark to silently accept default security settings
echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections
sudo apt-get install -y tcpdump wireshark

echo "[3/4] Installing Snort IDS..."
# Installs Snort with standard Ubuntu defaults
sudo apt-get install -y snort

echo "[4/4] Installing Python3 and Scapy..."
# Using apt for Scapy avoids "externally-managed-environment" pip errors on newer Ubuntu versions
sudo apt-get install -y python3 python3-pip python3-scapy

echo "=========================================="
echo "Provisioning Complete!"
echo "Next Step: Update /etc/snort/snort.conf with your specific HOME_NET variable."
echo "=========================================="
