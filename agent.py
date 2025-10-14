#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, subprocess, time, html

BASE_DIR = os.path.dirname(__file__)
ARCH = os.path.abspath(os.path.join(BASE_DIR, '../victim_app/archives'))
DB_DIR = os.path.abspath(os.path.join(BASE_DIR, '../victim_app'))
os.makedirs(ARCH, exist_ok=True)

def _sanitize_out(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.replace('\x00', '').replace('\r', '').strip()
    if len(s) > 2000:
        s = s[:2000] + '...[truncated]'
    return s

class Req(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # suppress default stderr logging
        return

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            if self.path.startswith('/archives'):
                files = sorted(os.listdir(ARCH), reverse=True)
                self._send(200, {"archives": files})
            else:
                self._send(404, {"error": "notfound"})
        except Exception as e:
            self._send(500, {"error": "exception", "detail": _sanitize_out(str(e))})

    def do_POST(self):
        try:
            if not self.path.startswith('/trigger'):
                self._send(404, {"error": "notfound"})
                return

            # Ignore any incoming JSON body or environment variable
            timestamp = str(int(time.time()))
            outfile = f"db_enc_{timestamp}.json"
            passphrase = "amanadmin"  # fixed demo key

            # Run encrypt command using fixed passphrase
            cmd = ['python3', os.path.join(DB_DIR, 'encrypt_db.py'), 'encrypt', outfile, passphrase]
            p = subprocess.run(cmd, cwd=DB_DIR, capture_output=True, text=True)

            out_text = _sanitize_out((p.stdout or '') + (p.stderr or ''))
            status = "ok" if p.returncode == 0 else "error"
            resp = {
                "status": status,
                "archive": outfile,
                "passphrase": passphrase,
                "out": out_text
            }
            self._send(200 if status == 'ok' else 500, resp)

        except Exception as e:
            self._send(500, {
                "status": "error",
                "error": "exception",
                "detail": _sanitize_out(str(e))
            })

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 6200), Req)
    print("Agent listening on http://127.0.0.1:6200")
    server.serve_forever()

