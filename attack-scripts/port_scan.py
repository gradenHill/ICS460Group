import sys
from scapy.all import IP, TCP, send

target_ip = "10.0.0.10"

def main():
    print(f"Scanning {target_ip} port 1-100")
	
    for port in range(1,101):
        pkt = IP(dst=target_ip) / TCP(
	    dport=port,
	    sport = 44444,
	    flags="S",
	    window=1234
	)
    try:
        send(pkt, verbose=False)
        print(f"[SCAN] Port {port}")
    except PermissionError:
        print("Permission Denied: run with sudo/root")
        sys.exit(1)
if __name__ == "__main__":
    main()
