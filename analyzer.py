from datetime import datetime
from scapy.all import rdpcap, TCP, IP
import re

def analyze_nids(pcap_file, alert_file):
    print(f"--- ANALYZING: {pcap_file} vs {alert_file} ---")
    
    # LOAD SNORT ALERT TIMES
    alert_times = []
    try:
        with open(alert_file, 'r') as f:
            for line in f:
                match = re.search(r'(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d{6})', line)
                if match:
                    alert_times.append(match.group(1).split('-')[1])
    except FileNotFoundError:
        print(f"Error: {alert_file} not found.")
        return

    # COMPARE TO PCAP
    packets = rdpcap(pcap_file)
    tp, fn, fp, tn = 0, 0, 0, 0
    
    for i, pkt in enumerate(packets):
        if IP in pkt and TCP in pkt:
            # LABEL MALICIOUS PACKETS: If Window is 1234, it's a known malicious packet from our script
            is_malicious = (pkt[TCP].window == 1234)
            
            # Did Snort alert?
            pkt_time = datetime.fromtimestamp(float(pkt.time)).strftime("%H:%M:%S")
            has_alert = any(time.startswith(pkt_time) for time in alert_times)

            if is_malicious and has_alert: 
                tp += 1
            elif is_malicious and not has_alert: 
                fn += 1
            elif not is_malicious and has_alert: 
                fp += 1
            else: 
                tn += 1

    # PRINT RESULTS
    total = tp + fn + fp + tn
    accuracy = (tp + tn) / total if total > 0 else 0
    
    print(f"\n[ RESULTS ]")
    print(f"Total Packets Processed: {total}")
    print(f"True Positives (Detected):  {tp}")
    print(f"False Negatives (Missed):   {fn}")
    print(f"False Positives (Wrong):    {fp}")
    print(f"True Negatives (Normal):    {tn}")
    print("-" * 30)
    print(f"DETECTION ACCURACY: {accuracy:.2%}")

if __name__ == "__main__":
    analyze_nids("capture.pcap", "alert")