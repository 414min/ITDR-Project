#!/usr/bin/env python3
import sys, json, time, os, datetime
OUT = os.path.expanduser('~/itdr_proj/fake_eve.json')

def make_alert(sid):
    return {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": "alert",
        "alert": {"signature_id": int(sid), "signature":"SIM", "category":"Demo", "severity":1},
        "src_ip":"10.0.0.5",
        "dest_ip":"10.164.178.76"
    }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: fake_alert_generator.py single|repeat SID [interval] [count]")
        sys.exit(1)
    mode = sys.argv[1]; sid = sys.argv[2]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if mode == 'single':
        with open(OUT, 'a') as f:
            f.write(json.dumps(make_alert(sid)) + "\\n")
        print("wrote SID", sid, "to", OUT)
    elif mode == 'repeat':
        interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        count = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        for i in range(count):
            with open(OUT, 'a') as f:
                f.write(json.dumps(make_alert(sid)) + "\\n")
            print(f"wrote {i+1}/{count} SID {sid}")
            time.sleep(interval)
    else:
        print("unknown mode")
