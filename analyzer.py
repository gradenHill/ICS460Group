from datetime import datetime
import json
import re
from scapy.all import rdpcap, IP, TCP

# Snort has weird timestamps. We need to convert them
def parse_snort_time(snort_time_str):
    current_year = datetime.now().year
    full_time_str = f"{current_year}/{snort_time_str}"
    dt = datetime.strptime(full_time_str, "%Y/%m/%d-%H:%M:%S.%f")
    return dt.timestamp()

def analyze_nids(alert_file, attack_log, pcap_file):
    print(f"=== ANALYZING SNORT PERFORMANCE ===")
    
    alert_times = []
    try:
        with open(alert_file, "r") as f:
            for line in f:
                # looking for this format: 04/24-15:20:01.123456
                match = re.match(r"^(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d+)", line)
                if match:
                    alert_times.append(parse_snort_time(match.group(1)))
    except FileNotFoundError:
        print(f"Error: {alert_file} not found.")
        return

    # Parse attack windows. Each window should get at least one alert.
    attack_windows = []
    try:
        with open(attack_log, "r") as f:
            for line in f:
                attack = json.loads(line)
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
    fp = 0
    tn = 0

    # every alert within a window is a true positive. any window without an alert is a false negative
    for atime in alert_times:
        is_in_window = any(win["start"] <= atime <= win["end"] for win in attack_windows)
        if is_in_window:
            tp += 1
        else:
            fp += 1
            print(f"[!] False Positive at {atime}")
    # Any window without an alert is a false negative
    for window in attack_windows:
        has_alert = any(window["start"] <= atime <= window["end"] for atime in alert_times)
        if not has_alert:
            fn += 1
            print(f"[-] False Negative: {window['type']} at {window['start']}")

    # Find packets outside of the window that were not alerted. These are True negatives
    try:
        packets = rdpcap(pcap_file)
        for pkt in packets:
            if pkt.haslayer(IP):
                pkt_time = float(pkt.time)
                isMalicious = any(win["start"] <= pkt_time <= win["end"] for win in attack_windows)
                if not isMalicious:
                    has_alert = any(abs(pkt_time - atime) < 0.1 for atime in alert_times)
                    if not has_alert:
                        tn += 1
    except Exception as e:
        print(f"Error: {e}")

    total_events = tp + fn + fp + tn
    print("\n--- FINAL RESULTS ---")
    print(f"False Negatives: {fn}")
    print(f"False Positives: {fp}")
    print(f"True Positives:  {tp}")
    print(f"True Negatives:  {tn}")
    print(f"ACCURACY:  {(tp + tn)/total_events:.2%}")

if __name__ == "__main__":
    analyze_nids("alert", "attack_log.json", "capture.pcap")