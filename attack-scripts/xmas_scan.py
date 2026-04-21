import sys
import random
import json
from scapy.all import IP, TCP, send
import time

target_ip ="10.0.0.10"

def main():
    start_time = time.time()
    print(f"Starting xmas scan against {target_ip}")
    ports = [21,22,23,25,53,80,110,139,443]
    for port in ports:
        pkt = IP(dst=target_ip) / TCP (
            sport=random.randint(1024, 65535),
            dport=port,
        flags="FPU",
        seq=random.randint(1000,99999),
    )
        send(pkt,verbose=False)
        print(f"[XMAS] Sent packet to port {port}")

    time.sleep(1)
    end_time = time.time()

    attack_event = {
        "attack_type": "Xmas Scan",
        "start": start_time,
        "end": end_time
    }
    with open("../attack_log.json", "a") as log:
        log.write(json.dumps(attack_event) + "\n")
    print("\n[+] Attack time window logged to attack_log.json")

if __name__ == "__main__":
    main()
