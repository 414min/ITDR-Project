#!/usr/bin/env python3
"""
log_watcher.py — follow a NDJSON log file and trigger the agent only for new lines
Starts by seeking to EOF so existing historical lines are ignored.
"""
import time, json, requests, os, sys

BASE = os.path.dirname(__file__)
FAKE_LOG = os.path.abspath(os.path.join(BASE, '..', 'fake_eve.json'))
AGENT_URL = "http://127.0.0.1:6200/trigger"
SID_TO_WATCH = 1000001
READ_SLEEP = 0.6
REQUEST_TIMEOUT = 4  # seconds

def ensure_file(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    # create file if missing
    open(path, 'a').close()

def follow(path):
    """
    Generator that yields new lines appended to `path`.
    Starts by seeking to EOF so we ignore historical lines.
    """
    with open(path, 'r') as fh:
        fh.seek(0, os.SEEK_END)   # <-- start at EOF (ignore existing content)
        while True:
            line = fh.readline()
            if not line:
                time.sleep(READ_SLEEP)
                continue
            yield line

def main():
    print("Watcher starting. Monitoring:", FAKE_LOG)
    ensure_file(FAKE_LOG)

    for raw in follow(FAKE_LOG):
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print("Watcher: JSON parse error:", e, "line:", line[:200])
            continue

        sid = obj.get('alert', {}).get('signature_id')
        if sid == SID_TO_WATCH:
            print(f"Detected demo SID {sid} - calling agent trigger")
            try:
                # use small timeout and post empty JSON body
                resp = requests.post(AGENT_URL, json={}, timeout=REQUEST_TIMEOUT)
                try:
                    j = resp.json()
                except Exception:
                    j = resp.text
                print("Agent response:", resp.status_code, j)
            except Exception as e:
                print("Failed to call agent:", e)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Watcher stopped by user")
        sys.exit(0)
    except Exception as e:
        print("Watcher fatal error:", e)
        sys.exit(1)

