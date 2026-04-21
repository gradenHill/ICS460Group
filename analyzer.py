from datetime import datetime
import json
import re

# Turn snort time stamp into a standard timestamp
def parse_snort_time(snort_time_str):
    current_year = datetime.now().year
    full_time_str = f"{current_year}/{snort_time_str}"
    dt = datetime.strptime(full_time_str, "%Y/%m/%d-%H:%M:%S.%f")
    return dt.timestamp()

def analyze_nids(alert_file, attack_log):
    print(f"--- ANALYZING: ALERTS ---")
    
    #LOAD SNORT ALERT TIMES
    alert_times = []
    try:
        with open(alert_file, "r") as f:
            for line in f:
                # Snort lines look like: 04/24-15:20:01.123456 [**] [1:100...
                match = re.match(r"^(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}\.\d+)", line)
                if match:
                    alert_times.append(parse_snort_time(match.group(1)))
    except FileNotFoundError:
        print(f"Error: {alert_file} not found.")
        return

    true_positives = 0
    false_negatives = 0


    with open(attack_log, "r") as f:
        for line in f:
            attack = json.loads(line)
            attack_start = attack["start"]
            attack_end = attack["end"]
            
            # Look for an alert within the window of the attack
            attack_caught = False
            for atime in alert_times:
                if attack_start <= atime <= attack_end:
                    attack_caught = True
                    break
            
            if attack_caught:
                true_positives += 1
                print(f"[+] DETECTED: {attack['attack_type']}")
            else:
                false_negatives += 1
                print(f"[-] MISSED:   {attack['attack_type']}")

    total_attacks = true_positives + false_negatives
    if total_attacks > 0:
        accuracy = (true_positives / total_attacks) * 100
        print("\n--- FINAL RESULTS ---")
        print(f"Total Attacks Run: {total_attacks}")
        print(f"True Positives (Caught): {true_positives}")
        print(f"False Negatives (Missed): {false_negatives}")
        print(f"DETECTION ACCURACY: {accuracy:.2f}%")
    else:
        print("No attacks found in the log.")

if __name__ == "__main__":
    analyze_nids("alert", "attack-scripts/attack_log.json")