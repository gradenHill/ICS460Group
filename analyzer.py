import sys
from scapy.all import rdpcap, TCP, IP
import re

def analyze_nids(pcap_file, alert_file):
    print(f"--- ANALYZING: {pcap_file} vs {alert_file} ---")
    
    # LOAD SNORT ALERT TIMES
    # format: 04/11-19:25:14.532123
    alert_times = []
    try:
        with open(alert_file, 'r') as f:
            for line in f:
                match = re.search(r'(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d{6})', line)
                if match:
                    # We store just the time part for matching
                    alert_times.append(match.group(1).split('-'))
    except FileNotFoundError:
        print("Error: alert.fast not found. Did you run Snort with -A fast?")
        return

    # COMPARE TO PCAP
    packets = rdpcap(pcap_file)
    tp, fn, fp, tn = 0, 0, 0, 0
    
    for i, pkt in enumerate(packets):
        if IP in pkt and TCP in pkt:
            # IF SENT FROM .20, IT'S MALICIOUS
            is_malicious = (pkt[IP].src == "10.0.0.20" and 
                            pkt[IP].dst == "10.0.0.10" and 
                            pkt[TCP].flags == "S")
            
            # CHECK IF SNORT ALERTED
            pkt_time = pkt.strftime("%H:%M:%S.%f")
            has_alert = any(time[:8] == pkt_time[:8] for time in alert_times)

            # COUNT 
            if is_malicious and has_alert: tp += 1
            elif is_malicious and not has_alert: fn += 1
            elif not is_malicious and has_alert: fp += 1
            elif not is_malicious and not has_alert: tn += 1

    # PRINT RESULTS
    total = tp + fn + fp + tn
    accuracy = (tp + tn) / total if total > 0 else 0
    
    print(f"\n[ RESULTS ]")
    print(f"Total Packets Processed: {total}")
    print(f"True Positives (Detected Attacks):  {tp}")
    print(f"False Negatives (Missed Attacks):   {fn}")
    print(f"False Positives (Wrong Alerts):     {fp}")
    print(f"True Negatives (Normal Traffic):    {tn}")
    print("-" * 30)
    print(f"DETECTION ACCURACY: {accuracy:.2%}")

if __name__ == "__main__":
    analyze_nids("capture.pcap", "alert")