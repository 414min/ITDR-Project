#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3, os, subprocess, json, datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'

BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE_DIR, 'data.db')
ARCH_DIR = os.path.join(BASE_DIR, 'archives')
ALERT_FILE = os.path.abspath(os.path.join(os.path.dirname(BASE_DIR), 'fake_eve.json'))
AUDIT_LOG = os.path.join(BASE_DIR, 'audit.log')
DEMO_KEY = "amanadmin"

os.makedirs(ARCH_DIR, exist_ok=True)

def log_audit(msg):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{ts} - {msg}\n")

def get_citizens():
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id,national_id,full_name,dob FROM citizens")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_archives():
    files = []
    try:
        for fn in sorted(os.listdir(ARCH_DIR), reverse=True):
            p = os.path.join(ARCH_DIR, fn)
            files.append({
                "name": fn,
                "size": os.path.getsize(p),
                "mtime": datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).isoformat() + "Z"
            })
    except Exception:
        pass
    return files

def read_alerts(limit=8):
    alerts = []
    try:
        if os.path.exists(ALERT_FILE):
            with open(ALERT_FILE,'r') as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines[-limit:]:
                try:
                    alerts.append(json.loads(line))
                except:
                    alerts.append({"raw": line})
    except Exception:
        pass
    return list(reversed(alerts))

def read_audit(limit=40):
    if not os.path.exists(AUDIT_LOG):
        return []
    with open(AUDIT_LOG,'r') as f:
        lines = [l.rstrip() for l in f if l.rstrip()]
    return lines[-limit:]

# ---------- Routes ----------

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        if u == 'admin' and p == '202518':
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    citizens = get_citizens()
    archives = get_archives()
    alerts = read_alerts(10)
    audit = read_audit(40)
    overview = {
        "citizen_count": len(citizens),
        "archive_count": len(archives),
        "last_encrypted": archives[0]["mtime"] if archives else None,
        "archives": archives
    }
    return render_template('admin.html', citizens=citizens, overview=overview, alerts=alerts, audit=audit)

@app.route('/restore', methods=['POST'])
def restore():
    archive = request.form.get('archive')
    passphrase = request.form.get('passphrase')
    if not archive:
        flash('No archive selected', 'danger')
        return redirect(url_for('dashboard'))
    arch_path = os.path.join(ARCH_DIR, archive)
    if not os.path.exists(arch_path):
        flash('Archive not found', 'danger')
        return redirect(url_for('dashboard'))
    if passphrase != DEMO_KEY:
        flash('Invalid passphrase', 'danger')
        log_audit(f"Failed restore attempt for {archive}: invalid passphrase")
        return redirect(url_for('dashboard'))

    p = subprocess.run(['python3', 'encrypt_db.py', 'decrypt', archive, passphrase],
                       cwd=BASE_DIR, capture_output=True, text=True)
    if p.returncode == 0:
        flash(f"Restore successful: {archive}", 'success')
        log_audit(f"Restore successful for {archive}")
    else:
        flash('Restore failed: ' + (p.stdout + p.stderr), 'danger')
        log_audit(f"Restore FAILED for {archive}: {p.stdout} {p.stderr}")
    return redirect(url_for('dashboard'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

# ---------- Main ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
@app.route('/logout')
def logout():
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

