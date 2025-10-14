#!/usr/bin/env python3
"""
Simple attack simulator for ITDR demo:
 - POSTS nothing to Flask anymore.
 - Appends a SURICATA-style NDJSON alert with SID 1000001 to the fake_eve.json
 - Use --force to always write an alert
"""
import argparse, os, datetime, json, time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAKE_EVE = os.path.join(PROJECT_ROOT, 'fake_eve.json')
PW_ATTEMPTS = ["wrongpass","password","123456","202518","or '1'='1'"]

def append_alert(sid=1000001):
    a = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": "alert",
        "alert": {"signature_id": sid, "signature": "SIM_DEMO_ATTACK", "category": "Demo", "severity": 1},
        "src_ip": "127.0.0.1",
        "dest_ip": "127.0.0.1"
    }
    os.makedirs(os.path.dirname(FAKE_EVE), exist_ok=True)
    with open(FAKE_EVE, "a") as f:
        f.write(json.dumps(a) + "\n")
    print("[+] wrote alert SID", sid, "->", FAKE_EVE)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--force', action='store_true', help='always write an alert')
    args = p.parse_args()

    print("Starting attack simulator -> sending login attempts (demo only)")
    # (This demo only simulates attempts locally; it does not POST to Flask anymore)
    fails = 0
    for pw in PW_ATTEMPTS:
        print("Tried admin /", pw)
        # for local demo we treat all as failed except the correct pass '202518'
        if pw != "202518":
            fails += 1
        time.sleep(0.2)

    if args.force or fails >= 1:
        print("[!] Multiple failed logins detected, writing alert.")
        append_alert(1000001)
    else:
        print("[*] No alert conditions met (demo)")

if __name__ == '__main__':
    main()
