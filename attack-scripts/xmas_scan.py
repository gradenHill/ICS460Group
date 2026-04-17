import sys
import random
from scapy.all import IP, TCP, send

target_ip ="10.0.0.10"

def main():
    print(f"Starting xmas scan against {target_ip}")
    ports = [21,22,23,25,53,80,110,139,443]
    for port in ports:
        pkt = IP(dst=target_ip) / TCP (
            sport=random.randint(1024, 65535),
            dport=port,
        flags="FPU",
        seq=random.randint(1000,99999),
        window=1234
    )
        send(pkt,verbose=False)
        print(f"[XMAS] Sent packet to port {port}")
if __name__ == "__main__":
    main()
