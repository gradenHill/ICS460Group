# ICS460Group: Network Intrusion Detection

## Group Members
* **Graden Hill:** Infrastructure Lead. Managed the Ubuntu Server, network namespace architecture, and Snort daemon configuration.
* **Trevor Reedy:** Attack Automation. Developed Python/Scapy scripts to simulate malicious TCP/IP traffic.
* **Kwesi Dacosta:** Data Analyst. Managed packet captures (PCAPs) and calculated empirical detection metrics (False Positives/Negatives).
* **Elise DeSimone:** Project Manager & Documentation. Maintained the GitHub repository and finalized the experimental reports.

## Repository Structure
* `/attack-scripts/`: Python and Scapy attack automation.
* `/snort-rules/`: Snort `local.rules` and configuration files.
* `/pcaps/`: Sample packet captures for rule verification.
* `/docs/`: Project proposal, architecture diagrams, and final reports.

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
* **Crucial:** Ensure you download the correct version for your CPU.
    * **Apple Silicon (M1/M2/M3):** Download the **ARM64** ISO.
    * **Intel/AMD (Windows/Old Macs):** Download the **AMD64 (x86_64)** ISO.

### 3. Create the VM
1.  Open your Hypervisor and create a new Linux VM using the ISO you just downloaded.
2.  **Resources:** Allocate at least **2GB RAM** and **20GB Storage**.
3.  **Network:** Set the network adapter to **Shared Network** or **NAT**.
4.  Complete the Ubuntu installation process (create your own username and password).

### 5. Clone the Repo
Run the following in your VM terminal:
```bash
git clone https://github.com/gradenHill/ICS460Group.git
```

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
8. Creates a tmux session with one pane in the `attacker` namespace, and one in the `target` namespace

To run the setup script, run the following commands, one at a time.
```bash
cd ICS460Group
chmod +x setup.sh
sudo ./setup.sh
```

### Left Pane: The Target
This pane automatically logs into the `target` namespace.
* **Run Snort:** `snort -A console -q -c ./snort.conf -i virtualEthernetTargetEnd -k none`
    * `-A console` sends alerts to the console if a rule is triggered
    * `-q` hides initialization text
    * `-c ./snort.conf` loads the snort configuration rules
    * `-i virtualEthernetTargetEnd` tells snort to listen on the cable to the network
    * `-k none` disables the checksum checks, which causes issues in virtual ethernet cables. 
* **Capture Traffic:** `tcpdump -i virtualEthernetTargetEnd -w capture.pcap`

### Right Pane: The Attacker
This pane automatically logs into the `attacker` namespace.
* **Test Ping Detection:** Run `ping -c 3 10.0.0.10`. The Target pane should respond.
* **Run Attacks (not yet written):** Navigate to `attack-scripts/` and execute Python/Scapy scripts targeting `10.0.0.10`.

## Running Scripts and Capture .pcaps

## Troubleshooting
1. After you git pull, the files might be owned by a different user. If Snort won't start, run this from the root of the repo:
`sudo chown -R $USER:$USER .`

2. If Git blocks you from pulling, run:
`git config --global --add safe.directory /home/$USER/ICS460Group`

## Analyzing .pcaps
To download the .pcaps, run the following command on your non-VM system:

```bash
scp [Ubuntu username]@[bridge IP address]:~/ICS460Group/capture.pcap ./
```

This will download capture.pcap so it can be analyzed with wireshark on your user interface.