from scapy.all import IP, TCP, send
import random
import os
import time

# Target Configuration
target_ip = "10.0.0.10"
target_port = 80

# We use a non-standard window size to allow our analyzer to accuretely detect malicious packets
MALICIOUS_WINDOW = 1234 

# We will run 10 cycles of 5 malicious packets followed by 1 safe packet
for cycle in range(10):
    print(f"\n--- Cycle {cycle + 1} ---")
    
    # 1. SEND MALICIOUS TRAFFIC (SYN Flood)
    for i in range(5):
        mal_packet = IP(dst=target_ip)/TCP(
            sport=random.randint(1024, 65535), 
            dport=target_port, 
            flags="S", 
            window=MALICIOUS_WINDOW
        )
        send(mal_packet, verbose=False)
        print(f"[!] MALICIOUS: SYN Packet sent (Watermark: {MALICIOUS_WINDOW})")

    # 2. SEND SAFE TRAFFIC (Normal User Activity)
    # curl uses a standard, valid TCP handshake
    os.system(f"curl -s --connect-timeout 1 {target_ip} > /dev/null")
    
    time.sleep(0.5)