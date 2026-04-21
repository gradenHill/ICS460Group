import sys
from scapy.all import IP, TCP, sr1, send
import json
import time

target_ip = "10.0.0.10"
common_ports=[20,21,22,23,25,53,67,68,69,80,110,123,135,137,138,139,143,161,389,443,445,993,995,1433,1521,3306,3389,5432,5900,8080]
def main():
    print(f"Scanning {target_ip} port 1-1025")

    start_time = time.time()
    
    open_ports = []	
    for port in common_ports:
        print(f"Scanning port{port}")
        pkt = IP(dst=target_ip) / TCP(
	    dport=port,
	    sport = 44444,
	    flags="S",
	)
        try:
            resp = sr1(pkt,timeout=0.3, verbose=False)
            if resp and resp.haslayer(TCP):
                flags=resp[TCP].flags
                if flags == 0x12:
                    open_ports.append(port)

                    rst = IP(dst=target_ip) / TCP(
                        dport=port,
                        sport=pkt[TCP].sport,
                        flags="R",
                    )
                    send(rst, verbose=False)
                    print(f"scanned port {port}")
        except PermissionError:
            print("Permission Denied: run with sudo/root")
            sys.exit(1)

    time.sleep(1)
    end_time = time.time()

    attack_event = {
        "attack_type": "Port Scan",
        "start": start_time,
        "end": end_time
    }
    
    print(f"\n Open Ports:{open_ports}")
    if open_ports:
        for port in open_ports:
            print(f"- {port}")
    else:
        print("No Open Ports")

    with open("../attack_log.json", "a") as log:
        log.write(json.dumps(attack_event) + "\n")
    print("\n[+] Attack time window logged to attack_log.json")

if __name__ == "__main__":
    main()
