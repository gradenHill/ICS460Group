from datetime import datetime
import json
import re
from scapy.all import rdpcap, IP, TCP

def parse_snort_time(snort_time_str):
    current_year = datetime.now().year
    full_time_str = f"{current_year}/{snort_time_str}"
    dt = datetime.strptime(full_time_str, "%Y/%m/%d-%H:%M:%S.%f")
    return dt.timestamp()

def analyze_nids(alert_file, attack_log, pcap_file):
    print(f"--- ANALYZING NIDS PERFORMANCE ---")
    
    alert_times = []
    try:
        with open(alert_file, "r") as f:
            for line in f:
                # Matches: 04/24-15:20:01.123456
                match = re.match(r"^(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d+)", line)
                if match:
                    alert_times.append(parse_snort_time(match.group(1)))
    except FileNotFoundError:
        print(f"Error: {alert_file} not found.")
        return

    attack_windows = []
    try:
        with open(attack_log, "r") as f:
            for line in f:
                attack = json.loads(line)
                # Expand window by 2 seconds to account for processing/disk delay
                attack_windows.append({
                    "start": attack["start"],
                    "end": attack["end"] + 2.0,
                    "type": attack["attack_type"]
                })
    except FileNotFoundError:
        print(f"Error: {attack_log} not found.")
        return

    tp = 0
    fn = 0
    
    for window in attack_windows:
        caught = any(window["start"] <= atime <= window["end"] for atime in alert_times)
        if caught:
            tp += 1
            print(f"[+] TP: Caught {window['type']}")
        else:
            fn += 1
            print(f"[-] FN: Missed {window['type']}")

    fp = 0
    for atime in alert_times:
        in_window = any(win["start"] <= atime <= win["end"] for win in attack_windows)
        if not in_window:
            fp += 1
            print(f"[!] FP: Alert triggered at {atime} outside of attack window")

    tn = 0
    try:
        packets = rdpcap(pcap_file)
        for pkt in packets:
            if pkt.haslayer(IP):
                pkt_time = float(pkt.time)
                
                is_malicious_packet = any(win["start"] <= pkt_time <= win["end"] for win in attack_windows)
                
                if not is_malicious_packet:
                    has_alert = any(abs(pkt_time - atime) < 0.1 for atime in alert_times)
                    if not has_alert:
                        tn += 1
    except Exception as e:
        print(f"Error processing PCAP: {e}")

    total_events = tp + fn + fp + tn
    print("\n--- FINAL RESULTS ---")
    print(f"True Positives:  {tp}")
    print(f"False Negatives: {fn}")
    print(f"False Positives: {fp}")
    print(f"True Negatives:  {tn}")
    print(f"ACCURACY:  {(tp + tn/total_events)}")

if __name__ == "__main__":
    analyze_nids("alert", "attack_log.json", "capture.pcap")