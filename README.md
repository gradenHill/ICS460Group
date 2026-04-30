# ICS460Group: Network Intrusion Detection

## Group Members
* **Graden Hill:** Infrastructure Lead. Managed the Ubuntu Server, network namespace architecture, and Snort rule configuration.
* **Trevor Reedy:** Attack Automation. Developed Python/Scapy scripts to simulate malicious TCP/IP traffic.
* **Kwesi Dacosta:** Managed packet captures (PCAPs) and calculated analytics (False/True Positives/Negatives).
* **Elise DeSimone:** Project Manager & Documentation. Maintained the GitHub repository, finalized reports, contributed heavily to `setup.sh` bash script.

## Repository Structure
* `/attack-scripts`: Python-Scapy attack automation.
* `/snort-rules`: Snort `local.rules` and configuration files.
* `analyzer.py`: Calculates Snort rule accuracy based on attack time windows and alert timestamps
* `setup.sh`: Verifies installations, creates virtual network, and sets up tmux display.
* `cleanUp.sh`: Removes all files created by previous runs to ensure analysis has a clean slate.


## Technical Architecture
* **Subnet:** `10.0.0.0/24`
* **Target Node (Server):** `10.0.0.10`
* **Attacker Node:** `10.0.0.20`
* **Connection:** A virtual Ethernet (`veth`) pair connecting the two isolated environments.

## First Time Setup

If you are setting up this demonstration for the first time, follow these steps to get the project running.

### 1. Install a Hypervisor
You need software to run the Virtual Machine (VM).
* **For ARM Macs (M1/M2/M3 chips):** Download and install UTM
* **For Windows or Intel-based Macs:** Download and install VirtualBox

### 2. Download Ubuntu Server
Download the **Ubuntu 22.04 LTS Server** ISO. 
* Ensure you download the correct version for your CPU.
    * **Apple Silicon (M1/M2/M3):** Download the **ARM64** ISO.
    * **Intel/AMD (Windows/Old Macs):** Download the **AMD64 (x86_64)** ISO.

### 3. Create the VM
1.  Open your Hypervisor and create a new Linux VM using the ISO you just downloaded.
2.  **Resources:** Allocate at least **2GB RAM** and **20GB Storage**.
3.  **Network:** Set the network adapter to **Shared Network** or **NAT**.
4.  Complete the Ubuntu installation process (create your own username and password).

### 5. Install this directory 
Ensure that this directory is saved to the VM.

## Launching the Attack Simulation Environment

### Load Up your Ubuntu VM
This Ubuntu VM should be configured with the settings listed above.

### Enable SSH & Find the Bridge IP Address (Optional)
This step is optional, but it allows you to use your native terminal to control the VM, enabling copy/pasting of commands from this README file.

```bash
sudo apt update && sudo apt install openssh-server -y
```
Run the following command to determine your bridge IP address
```bash
ip a
```
This will list multiple IP addresses. Ignore the "lo" address, as this is a loopback IP that only works within the VM itself.

The address you need is likely the only other address present. Look for an `eth*` or `enp*` address.
It should look something like `192.168.x.x` or `172.x.x.x`. This is the bridge address that you can use to access the VM from your native system.

In your native terminal, connect to the VM with running this command, replacing the necessary fields.
```bash
ssh [Ubuntu username]@[bridge IP address]
```

### Running the Setup Script
The setup script, `./setup.sh`, performs the following tasks:
1. Ensures the user has permission to the files in the directory
2. Sets `DEBIAN_FRONTEND=noninteractive`
3. Automatically answers Wireshark prompts
4. Ensures installation of
    - Snort: The Intrustion Detection System
    - tcpdump: Captures network Traffic
    - Wireshark: Analyzes network Traffic
    - Python: Used to run attack simulations
    - Scapy: Python library for easy network packet control
    - tmux: a terminal tool that allows us to run two terminal windows in our simple Ubuntu environment.
5. Launches `attacker` and `target` namespaces
6. Creates virtual ethernet cable to connect between the namespaces
7. Plugs in the cable and turns on the links
8. Creates a tmux session with one pane in the `attacker` namespace, and one in the `target` namespace.

Enter the root directory of this project. To run the setup script, run the following commands, one at a time.
```bash
chmod +x setup.sh
sudo ./setup.sh
```

### Left Pane: Target Namespace
This pane automatically logs into the `target` namespace.
These commands can be automatically typed by pressing the "up" key.
* **Capture Traffic:** `tcpdump -i veth-target -w capture.pcap &`
* **Run Snort:** `stdbuf -oL snort -A console -q -U -c ./snort.conf -i veth-target | tee alert`

### Right Pane: Attacker Namespace
This pane automatically logs into the `attacker` namespace.
* **Run Attacks:**
    * `python3 syn_flood.py`
    * `python3 xmas_scan.py`
    * `python3 port_scan.py`

### Top Pane: Management Pane
* **Kill Snort:** `sudo pkill -9 snort`
* **Run Analysis:** `python3 analyzer.py`
* **Reset Before Next Test:** `./cleanUp.sh`

## Troubleshooting
After you git pull, the files might be owned by a different user. If Snort won't start, run this from the root of the repo:
`sudo chown -R $USER:$USER .`