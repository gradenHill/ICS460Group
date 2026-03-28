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
* **Target Node (Server):** `10.0.0.10` (Managed via the `target` namespace)
* **Attacker Node:** `10.0.0.20` (Managed via the `attacker` namespace)
* **Connection:** A virtual Ethernet (`veth`) pair connecting the two isolated environments.

## First Time Setup

If you are starting with a blank computer, follow these steps to get your lab environment running.

### 1. Install a Hypervisor
You need software to run the Virtual Machine (VM).
* **For Mac (M1/M2/M3 chips):** Download and install [UTM](https://getutm.app/).
* **For Windows or Intel-based Macs:** Download and install [VirtualBox](https://www.virtualbox.org/).

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

### 4. Enable SSH & Get the IP (Optional, but allows you to use your native terminal to control the VM)
Once logged into your new Ubuntu VM, run these commands to allow your host computer to connect to it (this makes copy/pasting possible):
```bash
sudo apt update && sudo apt install openssh-server -y
ip a
```
Note the IP address listed (e.g., 192.168.x.x)
Then in your Mac/PC terminal, connect by running this command, replacing the necessary fields.
```bash
ssh [your username here]@[noted IP address here]
```

### 5. Generate a GitHub Personal Access Token (PAT)
You cannot use your GitHub password in the terminal.
1.  Go to GitHub **Settings** > **Developer Settings** > **Personal Access Tokens** > **Tokens (classic)**.
2.  Generate a new token with the **'repo'** scope checked. **Copy it and save it somewhere safe.**

### 6. Clone the Repo
Now, run the following in your VM terminal:
```bash
git clone [https://github.com/gradenHill/ICS460Group.git](https://github.com/gradenHill/ICS460Group.git)
```

## How to Run
Run the following commands:
```bash
cd ICS460Group
chmod +x setup.sh
sudo ./setup.sh
```
Running `setup.sh` automatically launches a **tmux** session with two active panes:

### **Left Pane: The Target (Graden/Kwesi)**
This pane is automatically logged into the `target` namespace.
* **Run Snort:** `sudo snort -A console -q -c /etc/snort/snort.conf -i veth-tar`
* **Capture Traffic:** `sudo tcpdump -i veth-tar -w capture.pcap`

### **Right Pane: The Attacker (Trevor)**
This pane is automatically logged into the `attacker` namespace.
* **Run Attacks:** Navigate to `attack-scripts/` and execute Python/Scapy scripts targeting `10.0.0.10`.
