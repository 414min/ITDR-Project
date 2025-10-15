#!/usr/bin/env python3
"""
Simple demo encrypt/decrypt for the sqlite file using AES-256-CBC via Python cryptography.
Archive format: JSON with base64 ciphertext and salt/iv.
"""
import sys, os, json, base64, sqlite3
from hashlib import pbkdf2_hmac
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

DB='data.db'
ARCH_DIR='archives'

def derive_key(passphrase, salt):
    return pbkdf2_hmac('sha256', passphrase.encode(), salt, 200000, dklen=32)

def pad(b):
    padlen = 16 - (len(b) % 16)
    return b + bytes([padlen])*padlen

def unpad(b):
    return b[:-b[-1]]

def encrypt(outfile, passphrase):
    salt = get_random_bytes(16)
    key = derive_key(passphrase, salt)
    iv = get_random_bytes(16)
    with open(DB,'rb') as f:
        data = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data))
    payload = {'salt': base64.b64encode(salt).decode(), 'iv': base64.b64encode(iv).decode(), 'ct': base64.b64encode(ct).decode()}
    outpath = os.path.join(ARCH_DIR, outfile)
    with open(outpath,'w') as o:
        o.write(json.dumps(payload))
    # wipe DB (replace with empty structure)
    conn=sqlite3.connect(DB); cur=conn.cursor()
    cur.execute("DROP TABLE IF EXISTS citizens")
    cur.execute("CREATE TABLE citizens (id INTEGER PRIMARY KEY, national_id TEXT, full_name TEXT, dob TEXT)")
    conn.commit(); conn.close()
    print("OK: encrypted to", outpath)

def decrypt(infile, passphrase):
    path=os.path.join(ARCH_DIR, infile)
    with open(path,'r') as f:
        obj=json.load(f)
    salt=base64.b64decode(obj['salt']); iv=base64.b64decode(obj['iv']); ct=base64.b64decode(obj['ct'])
    key=derive_key(passphrase, salt)
    cipher=AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct))
    # restore file
    with open(DB,'wb') as f: f.write(pt)
    print("OK: restored to", DB)

if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else ''
    if cmd=='encrypt':
        encrypt(sys.argv[2], sys.argv[3])
    elif cmd=='decrypt':
        decrypt(sys.argv[2], sys.argv[3])
    else:
        print("Usage: encrypt_db.py encrypt <outfile> <passphrase> OR decrypt <outfile> <passphrase>")
