# +═════════════════════════════════════════════════════════════════════════+
# ║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
# ║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
# ║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
# ║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
# ║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
# ║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
# ║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
# ║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
# ║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
# ║                                                                         ║
# +═════════════════════════════════════════════════════════════════════════+
# ║                               by MKultra69                              ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                      https://github.com/MKultra6969                     ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                  mk69.su                                ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                VERSION 0.5                              ║
# ║             Не очень стабильная версия, но база работает.               ║
# ║             В случае багов/недочётов создайте issue на github           ║
# +═════════════════════════════════════════════════════════════════════════+


import argparse
import tempfile
import sys
import os
import shutil
import logging
import random
import time
import json
import socket
import subprocess
import platform
import base64
import requests
import psutil
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace
from threading import Lock

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROTO_HINTS = ("vless://", "vmess://", "trojan://", "hysteria2://", "hy2://", "ss://")

BASE64_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-")

URL_FINDER = re.compile(
    r'(?:vless|vmess|trojan|hysteria2|hy2)://[^\s"\'<>]+|(?<![A-Za-z0-9+])ss://[^\s"\'<>]+',
    re.IGNORECASE
)

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = RESET = MAGENTA = BLUE = WHITE = LIGHTBLACK_EX = ""
        LIGHTGREEN_EX = LIGHTRED_EX = LIGHTYELLOW_EX = LIGHTCYAN_EX = LIGHTMAGENTA_EX = ""
    class Style:
        BRIGHT = RESET_ALL = ""
    def init(autoreset=True): pass

def clean_url(url):
    url = url.strip()
    url = url.replace('\ufeff', '').replace('\u200b', '')
    url = url.replace('\n', '').replace('\r', '')
    return url

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO, datefmt='%H:%M:%S')
print_lock = Lock()

TEMP_DIR = tempfile.mkdtemp()
OS_SYSTEM = platform.system().lower()
CORE_PATH = "" # оставь пустым если ядро лежит прям в обнимку с скриптом
CTRL_C = False

LOGO_ASCII = r"""
+═════════════════════════════════════════════════════════════════════════+
║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
║                                                                         ║
+═════════════════════════════════════════════════════════════════════════+
║                               MKultra69                                 ║
+═════════════════════════════════════════════════════════════════════════+
"""

# ------------------------------ ДАЛЬШЕ БОГА НЕТ ------------------------------

def safe_print(msg):
    with print_lock:
        print(msg)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def split_list(lst, n):
    if n <= 0: return []
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def try_decode_base64(text):
    raw = text.strip()
    if not raw:
        return raw

    if any(marker in raw for marker in PROTO_HINTS):
        return raw

    compact = re.sub(r'\s+', '', raw)
    if not compact or not set(compact) <= BASE64_CHARS:
        return raw

    missing_padding = len(compact) % 4
    if missing_padding:
        compact += "=" * (4 - missing_padding)

    for decoder in (base64.b64decode, base64.urlsafe_b64decode):
        try:
            decoded = decoder(compact).decode("utf-8", errors="ignore")
        except Exception:
            continue
        if any(marker in decoded for marker in PROTO_HINTS):
            return decoded
    return raw

def _payload_variants(blob):
    clean_blob = blob.strip()
    if not clean_blob:
        return set()

    variants = {clean_blob}
    
    decoded_blob = try_decode_base64(clean_blob)
    
    if decoded_blob and decoded_blob != clean_blob:
        variants.add(decoded_blob)
    for line in clean_blob.splitlines():
        line = line.strip()
        if not line:
            continue
        maybe_decoded = try_decode_base64(line)
        if maybe_decoded and maybe_decoded != line:
            variants.add(maybe_decoded)
            
    return variants

def parse_content(text):
    unique_links = set()
    raw_hits = 0

    for payload in _payload_variants(text):
        matches = URL_FINDER.findall(payload)
        raw_hits += len(matches)
        for item in matches:
            cleaned = clean_url(item.rstrip(';,)]}'))
            if cleaned and len(cleaned) > 15:
                unique_links.add(cleaned)

    return list(unique_links), raw_hits or len(unique_links)

def fetch_url(url):
    try:
        safe_print(f"{Fore.CYAN}>> Загрузка URL: {url}{Style.RESET_ALL}")
        resp = requests.get(url, timeout=15, verify=False)
        if resp.status_code == 200:
            links, count = parse_content(resp.text)
            return links
        else:
            safe_print(f"{Fore.RED}>> Ошибка скачивания: HTTP {resp.status_code}{Style.RESET_ALL}")
    except Exception as e:
        safe_print(f"{Fore.RED}>> Ошибка URL: {e}{Style.RESET_ALL}")
    return []
    
    
    
def parse_vless(url):
    try:
        url = clean_url(url)
        if not url.startswith("vless://"): return None

        if '#' in url:
            main_part, tag = url.split('#', 1)
            tag = urllib.parse.unquote(tag).strip()
        else:
            main_part = url
            tag = "vless"

        match = re.search(r'vless://([^@]+)@([^:]+):(\d+)', main_part)
        
        if not match:
            return None

        uuid = match.group(1).strip()
        address = match.group(2).strip()
        port = int(match.group(3))

        params = {}
        if '?' in main_part:
            query = main_part.split('?', 1)[1]
            params = urllib.parse.parse_qs(query)

        def get_p(key, default=""):
            val = params.get(key, [default])
            return val[0] if val else default

        sec = get_p("security", "none")
        pbk_val = get_p("pbk", "")
        
        if pbk_val and sec == "tls":
            sec = "reality"

        return {
            "protocol": "vless",
            "uuid": uuid,
            "address": address,
            "port": port,
            "encryption": get_p("encryption", "none"),
            "type": get_p("type", "tcp"),
            "security": sec,
            "path": urllib.parse.unquote(get_p("path", "")),
            "host": get_p("host", ""),
            "sni": get_p("sni", ""),
            "fp": get_p("fp", ""),
            "alpn": get_p("alpn", ""),
            "serviceName": get_p("serviceName", ""),
            "mode": get_p("mode", ""),
            "pbk": get_p("pbk", ""),
            "sid": get_p("sid", ""),
            "flow": get_p("flow", ""),
            "tag": tag
        }
    except Exception as e:
        safe_print(f"{Fore.RED}[VLESS ERROR] {e}{Style.RESET_ALL}")
        return None

def parse_vmess(url):
    try:
        url = clean_url(url)
        if not url.startswith("vmess://"): return None

        if '@' in url:
            if '#' in url:
                main_part, tag = url.split('#', 1)
                tag = urllib.parse.unquote(tag).strip()
            else:
                main_part = url
                tag = "vmess"

            match = re.search(r'vmess://([^@]+)@([^:]+):(\d+)', main_part)
            if match:
                uuid = match.group(1).strip()
                address = match.group(2).strip()
                port = int(match.group(3))

                params = {}
                if '?' in main_part:
                    query = main_part.split('?', 1)[1]
                    params = urllib.parse.parse_qs(query)

                def get_p(key, default=""):
                    val = params.get(key, [default])
                    return val[0] if val else default
                
                try: aid = int(get_p("aid", "0"))
                except: aid = 0
                
                raw_path = get_p("path", "")
                final_path = urllib.parse.unquote(raw_path)

                return {
                    "protocol": "vmess",
                    "uuid": uuid,
                    "address": address,
                    "port": port,
                    "type": get_p("type", "tcp"),
                    "security": get_p("security", "none"),
                    "path": final_path,
                    "host": get_p("host", ""),
                    "sni": get_p("sni", ""),
                    "fp": get_p("fp", ""),
                    "alpn": get_p("alpn", ""),
                    "serviceName": get_p("serviceName", ""),
                    "aid": aid,
                    "scy": get_p("encryption", "auto"),
                    "tag": tag
                }

        content = url[8:]
        if '#' in content:
            b64, tag = content.rsplit('#', 1)
            tag = urllib.parse.unquote(tag).strip()
        else:
            b64 = content
            tag = "vmess"
            
        missing_padding = len(b64) % 4
        if missing_padding: b64 += '=' * (4 - missing_padding)
        
        try:
            decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
            data = json.loads(decoded)
            return {
                "protocol": "vmess",
                "uuid": data.get("id"),
                "address": data.get("add"),
                "port": int(data.get("port", 0)),
                "aid": int(data.get("aid", 0)),
                "type": data.get("net", "tcp"),
                "security": data.get("tls", "") if data.get("tls") else "none",
                "path": data.get("path", ""),
                "host": data.get("host", ""),
                "sni": data.get("sni", ""),
                "fp": data.get("fp", ""),
                "alpn": data.get("alpn", ""),
                "scy": data.get("scy", "auto"),
                "tag": data.get("ps", tag)
            }
        except:
            pass

        return None
    except Exception as e:
        safe_print(f"{Fore.RED}[VMESS ERROR] {e}{Style.RESET_ALL}")
        return None
    
def parse_trojan(url):
    try:
        if '#' in url:
            url_clean, tag = url.split('#', 1)
        else:
            url_clean = url
            tag = "trojan"
        
        parsed = urllib.parse.urlparse(url_clean)
        params = urllib.parse.parse_qs(parsed.query)
        
        return {
            "protocol": "trojan",
            "uuid": parsed.username,
            "address": parsed.hostname,
            "port": parsed.port,
            "security": params.get("security", ["tls"])[0],
            "sni": params.get("sni", [""])[0] or params.get("peer", [""])[0],
            "type": params.get("type", ["tcp"])[0],
            "path": params.get("path", [""])[0],
            "host": params.get("host", [""])[0],
            "tag": urllib.parse.unquote(tag).strip()
        }
    except: return None

def parse_ss(url):
    try:
        if '#' in url:
            url_clean, tag = url.split('#', 1)
        else:
            url_clean = url
            tag = "ss"
        
        parsed = urllib.parse.urlparse(url_clean)
        
        if '@' in url_clean:
            userinfo = parsed.username
            try:
                if ':' not in userinfo:
                    missing_padding = len(userinfo) % 4
                    if missing_padding: userinfo += '=' * (4 - missing_padding)
                    decoded_info = base64.b64decode(userinfo).decode('utf-8')
                else:
                    decoded_info = userinfo
            except:
                decoded_info = userinfo
            
            method, password = decoded_info.split(':', 1)
            address = parsed.hostname
            port = parsed.port
        else:
            b64 = url_clean.replace("ss://", "")
            missing_padding = len(b64) % 4
            if missing_padding: b64 += '=' * (4 - missing_padding)
            decoded = base64.b64decode(b64).decode('utf-8')
            method_pass, addr_port = decoded.rsplit('@', 1)
            method, password = method_pass.split(':', 1)
            address, port = addr_port.rsplit(':', 1)
            port = int(port)

        return {
            "protocol": "shadowsocks",
            "address": address,
            "port": port,
            "method": method,
            "password": password,
            "tag": urllib.parse.unquote(tag).strip()
        }
    except: return None

def parse_hysteria2(url):
    try:
        url = url.replace("hy2://", "hysteria2://")
        if '#' in url:
            url_clean, tag = url.split('#', 1)
        else:
            url_clean = url
            tag = "hy2"
            
        parsed = urllib.parse.urlparse(url_clean)
        params = urllib.parse.parse_qs(parsed.query)
        
        return {
            "protocol": "hysteria2",
            "uuid": parsed.username,
            "address": parsed.hostname,
            "port": parsed.port,
            "sni": params.get("sni", [""])[0],
            "insecure": params.get("insecure", ["0"])[0] == "1",
            "tag": urllib.parse.unquote(tag).strip()
        }
    except: return None

    
def get_proxy_tag(url):
    try:
        url = clean_url(url)
        if '#' in url:
            _, tag = url.rsplit('#', 1)
            return urllib.parse.unquote(tag).strip()
    except: 
        pass
    
    try:
        if url.startswith("vmess"): 
            res = parse_vmess(url)
            if res: return res.get('tag', 'vmess')
    except: pass
    
    return "proxy"

def create_config_file(proxy_url, local_port, work_dir):
    proxy_url = clean_url(proxy_url)
    proxy_conf = None
    
    if proxy_url.startswith("vless://"): proxy_conf = parse_vless(proxy_url)
    elif proxy_url.startswith("vmess://"): proxy_conf = parse_vmess(proxy_url)
    elif proxy_url.startswith("trojan://"): proxy_conf = parse_trojan(proxy_url)
    elif proxy_url.startswith("ss://"): proxy_conf = parse_ss(proxy_url)
    elif proxy_url.startswith("hy"): proxy_conf = parse_hysteria2(proxy_url)
    
    if not proxy_conf: 
        return None, "Parsing Failed"

    streamSettings = {}
    
    if proxy_conf["protocol"] in ["vless", "vmess", "trojan"]:
        streamSettings = {
            "network": proxy_conf.get("type", "tcp"),
            "security": proxy_conf.get("security", "none")
        }
        
        if streamSettings["security"] == "tls":
            streamSettings["tlsSettings"] = {
                "serverName": proxy_conf.get("sni") or proxy_conf.get("host"),
                "allowInsecure": True,
                "fingerprint": proxy_conf.get("fp", "")
            }
        elif streamSettings["security"] == "reality":
             if "xray" not in CORE_PATH.lower(): return None, "Reality requires Xray"
             streamSettings["realitySettings"] = {
                "publicKey": proxy_conf.get("pbk"),
                "shortId": proxy_conf.get("sid"),
                "serverName": proxy_conf.get("sni"),
                "fingerprint": proxy_conf.get("fp", "chrome")
            }

        if streamSettings["network"] == "ws":
            streamSettings["wsSettings"] = {
                "path": proxy_conf.get("path", "/"),
                "headers": {"Host": proxy_conf.get("host", "")}
            }
            
        elif streamSettings["network"] == "grpc":
            svc_name = proxy_conf.get("serviceName", "")
            if not svc_name:
                svc_name = proxy_conf.get("path", "")
            if not svc_name:
                svc_name = "grpc" # Заглушка, впринцепе ваще похуй че туда писать.
            
            streamSettings["grpcSettings"] = {
                "serviceName": svc_name,
                "multiMode": False
            }

    if proxy_conf["protocol"] == "hysteria2":
        streamSettings = {
            "security": "tls",
            "tlsSettings": {
                "serverName": proxy_conf.get("sni", ""),
                "allowInsecure": proxy_conf.get("insecure", False)
            }
        }

    outbound = {
        "protocol": proxy_conf["protocol"],
        "streamSettings": streamSettings
    }

    if proxy_conf["protocol"] == "shadowsocks":
        legacy_methods = ["chacha20-ietf", "chacha20", "rc4-md5", "aes-128-ctr", "aes-192-ctr", "aes-256-ctr", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb"]
        curr_method = proxy_conf["method"].lower()
        if curr_method == "chacha20-ietf": curr_method = "chacha20-ietf-poly1305" 
        
        outbound["settings"] = {
            "servers": [{
                "address": proxy_conf["address"],
                "port": int(proxy_conf["port"]),
                "method": curr_method,
                "password": proxy_conf["password"]
            }]
        }
        outbound.pop("streamSettings", None)

    elif proxy_conf["protocol"] == "trojan":
        outbound["settings"] = {
            "servers": [{
                "address": proxy_conf["address"],
                "port": int(proxy_conf["port"]),
                "password": proxy_conf["uuid"]
            }]
        }
        
    elif proxy_conf["protocol"] == "hysteria2":
        outbound["settings"] = {
            "vnext": [{
                "address": proxy_conf["address"],
                "port": int(proxy_conf["port"]),
                "users": [{"password": proxy_conf["uuid"]}]
            }]
        }

    else:
        outbound["settings"] = {
            "vnext": [{
                "address": proxy_conf["address"],
                "port": int(proxy_conf["port"]),
                "users": [{
                    "id": proxy_conf["uuid"],
                    "alterId": proxy_conf.get("aid", 0),
                    "encryption": "none",
                    "flow": proxy_conf.get("flow", "") 
                }]
            }]
        }

    full_config = {
        "log": {"loglevel": "none"}, 
        "inbounds": [{
            "port": local_port,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {"udp": True}
        }],
        "outbounds": [outbound]
    }

    filename = os.path.join(work_dir, f"config_{local_port}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(full_config, f, indent=2)
    except Exception as e:
        return None, str(e)
    return filename, None

def run_core(core_path, config_path):
    cmd = [core_path, "run", "-c", config_path] if "xray" in core_path.lower() else [core_path, "-c", config_path]
    startupinfo = None
    if OS_SYSTEM == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, startupinfo=startupinfo)
    except: return None

def kill_core(proc):
    if not proc: return
    try:
        if psutil:
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                try: child.kill() 
                except: pass
            parent.kill()
        else:
            proc.terminate()
            try: proc.wait(timeout=0.2)
            except: proc.kill()
    except: pass

def check_connection(local_port, domain, timeout):
    proxies = {
        'http': f'socks5://127.0.0.1:{local_port}',
        'https': f'socks5://127.0.0.1:{local_port}'
    }
    try:
        start = time.time()
        resp = requests.get(domain, proxies=proxies, timeout=timeout, verify=False)
        end = time.time()
        if resp.status_code < 400:
            return round((end - start) * 1000), None
        else:
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

def Checker(proxyList, localPort, testDomain, timeOut, t2exec, t2kill):
    liveProxy = []
    
    for url in proxyList:
        if CTRL_C: break
        
        tag = get_proxy_tag(url)
        configName, err_msg = create_config_file(url, localPort, TEMP_DIR)
        
        if not configName:
            safe_print(f"{Fore.RED}[Skip] {tag[:15]}.. -> {err_msg}{Style.RESET_ALL}")
            continue

        proc = run_core(CORE_PATH, configName)
        if not proc:
            safe_print(f"{Fore.RED}[Err] Core start fail{Style.RESET_ALL}")
            try: os.remove(configName)
            except: pass
            continue

        time.sleep(t2exec)
        
        if proc.poll() is not None:
            safe_print(f"{Fore.RED}[Dead] {tag[:15]}.. -> Core crashed{Style.RESET_ALL}")
            try: os.remove(configName)
            except: pass
            continue
            
        ping, error_reason = check_connection(localPort, testDomain, timeOut)
        
        if ping:
            safe_print(f"{Fore.GREEN}[LIVE] {ping}ms | {tag}{Style.RESET_ALL}")
            liveProxy.append((url, ping))
        else:
            short_err = str(error_reason)
            if "SOCKSHTTPSConnectionPool" in short_err: short_err = "Conn Error"
            elif "Read timed out" in short_err: short_err = "Timeout"
            safe_print(f"{Fore.YELLOW}[Dead] {tag[:15]}.. -> {short_err}{Style.RESET_ALL}")

        kill_core(proc)
        time.sleep(t2kill)
        try: os.remove(configName)
        except: pass

    return liveProxy

def run_logic(args):
    global CORE_PATH, CTRL_C
    
    CORE_PATH = shutil.which(args.core)
    if not CORE_PATH:
        candidates = ["xray.exe", "xray", "v2ray.exe", "v2ray", "bin/xray.exe", "bin/xray"]
        for c in candidates:
             if os.path.exists(c):
                 CORE_PATH = os.path.abspath(c)
                 break
    
    if not CORE_PATH:
        print(f"{Fore.RED}\n[ERROR] Ядро (xray/v2ray) не найдено! Убедитесь, что файл рядом.{Style.RESET_ALL}")
        return
        
    logging.info(f"Core detected: {CORE_PATH}")
    
    lines = set()
    total_found_raw = 0
    
    if args.file:
        fpath = args.file.strip('"')
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                parsed, count = parse_content(f.read())
                total_found_raw += count
                lines.update(parsed)
        else:
            print(f"{Fore.RED}Файл не найден: {fpath}{Style.RESET_ALL}")

    if args.url:
        links = fetch_url(args.url)
        lines.update(links)

    if args.reuse and os.path.exists(args.output):
        with open(args.output, 'r', encoding='utf-8') as f:
            parsed, count = parse_content(f.read())
            lines.update(parsed)

    full = list(lines)
    
    if total_found_raw > 0:
        duplicates = total_found_raw - len(full)
        if duplicates > 0:
            print(f"{Fore.YELLOW}Найдено: {total_found_raw}. Дубликатов: {duplicates}. К проверке: {len(full)}{Style.RESET_ALL}")
        else:
             print(f"{Fore.CYAN}Загружено прокси: {len(full)}{Style.RESET_ALL}")
    
    if not full:
        print(f"{Fore.RED}Нет прокси для проверки.{Style.RESET_ALL}")
        return

    if args.shuffle: random.shuffle(full)
    if args.number: full = full[:args.number]

    threads = min(args.threads, len(full))
    ports = []
    p = args.lport
    while len(ports) < threads:
        if not is_port_in_use(p):
            ports.append(p)
        p += 1
    
    chunks = list(split_list(full, threads))
    results = []
    
    print(f"{Fore.MAGENTA}Запуск {threads} потоков...{Style.RESET_ALL}\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for i in range(threads):
            if i < len(chunks) and chunks[i]:
                futures.append(executor.submit(Checker, chunks[i], ports[i], args.domain, args.timeout, args.t2exec, args.t2kill))
        
        try:
            for f in as_completed(futures):
                results.extend(f.result())
        except KeyboardInterrupt:
            CTRL_C = True
            print(f"\n{Fore.RED}!!! Остановка по CTRL+C !!!{Style.RESET_ALL}")
            executor.shutdown(wait=False)

    results.sort(key=lambda x: x[1])
    
    with open(args.output, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(r[0] + '\n')
            
    print(f"\n{Fore.LIGHTGREEN_EX}Готово! Рабочих: {len(results)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Результат сохранен в: {Style.BRIGHT}{args.output}{Style.RESET_ALL}")

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + LOGO_ASCII + Style.RESET_ALL)
    print(f"{Fore.MAGENTA}          by mkultra69  |  https://t.me/MKextera{Style.RESET_ALL}")
    print(Fore.LIGHTBLACK_EX + "─"*75 + Style.RESET_ALL)

def interactive_menu():
    while True:
        print_banner()
        print(f"{Fore.LIGHTWHITE_EX} [ ИСТОЧНИК ]{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}1.{Style.RESET_ALL} Загрузить из файла (.txt)")
        print(f"  {Fore.GREEN}2.{Style.RESET_ALL} Загрузить по ссылке (URL)")
        print(f"  {Fore.GREEN}3.{Style.RESET_ALL} Перепроверить (sortedProxy.txt)")
        print(f"\n{Fore.LIGHTWHITE_EX} [ ДЕЙСТВИЕ ]{Style.RESET_ALL}")
        print(f"  {Fore.RED}0.{Style.RESET_ALL} Выход")
        print(Fore.LIGHTBLACK_EX + "─"*75 + Style.RESET_ALL)
        
        ch = input(f"{Fore.YELLOW} > Выбор: {Style.RESET_ALL}").strip()
        
        defaults = {
            "file": None, "url": None, "reuse": False,
            "domain": 'http://www.gstatic.com/generate_204', # домен для теста
            "timeout": 3, "lport": 1080, "threads": 20, 
            "core": "xray", "t2exec": 0.8, "t2kill": 0.1, 
            "output": 'sortedProxy.txt', "shuffle": False, "number": None, # sortedProxy.txt
            "menu": True
        }
        
        if ch == '0':
            print(f"\n{Fore.MAGENTA}ПОДПИШИСЬ https://t.me/MKextera{Style.RESET_ALL}")
            sys.exit()
        
        if ch == '1':
            print()
            f_input = input(f"{Fore.CYAN} [?] Путь к файлу: {Style.RESET_ALL}").strip('"')
            if not f_input: continue
            defaults["file"] = f_input
            
        elif ch == '2':
            print()
            u_input = input(f"{Fore.CYAN} [?] URL ссылки: {Style.RESET_ALL}").strip()
            if not u_input: continue
            defaults["url"] = u_input
            
        elif ch == '3':
            defaults["reuse"] = True
            
        else:
            continue
        
        print(f"\n{Fore.LIGHTBLACK_EX}--- Настройки (Enter = стандартно) ---{Style.RESET_ALL}")
        try:
            th = input(f" Потоки [{Fore.GREEN}20{Style.RESET_ALL}]: ").strip()
            if th: defaults["threads"] = int(th)
            
            to = input(f" Таймаут [{Fore.GREEN}3{Style.RESET_ALL}]: ").strip()
            if to: defaults["timeout"] = int(to)
        except: pass

        args = SimpleNamespace(**defaults)
        
        print(f"\n{Fore.YELLOW}>>> Инициализация проверки...{Style.RESET_ALL}")
        time.sleep(0.5)
        
        try:
            run_logic(args)
        except Exception as e:
            print(f"{Fore.RED}CRITICAL ЕГГОГ: {e}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Нажмите Enter чтобы вернуться в меню...{Style.RESET_ALL}")
        input()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--menu", action="store_true")
    parser.add_argument("-f", "--file")
    parser.add_argument("-u", "--url")
    parser.add_argument("--reuse", action="store_true")
    parser.add_argument("-t", "--timeout", type=int, default=3)
    parser.add_argument("-l", "--lport", type=int, default=1080)
    parser.add_argument("-T", "--threads", type=int, default=20)
    parser.add_argument("-c", "--core", default="xray")
    parser.add_argument("--t2exec", type=float, default=0.8)
    parser.add_argument("--t2kill", type=float, default=0.1)
    parser.add_argument("-o", "--output", default="sorted.txt") # тут вот тоже ручками можно аутпут файлик прописать
    parser.add_argument("-d", "--domain", default='http://www.gstatic.com/generate_204') # а это ссылочка через которую все прокси чекаются, тоже при желании менять
    parser.add_argument("-s", "--shuffle", action='store_true')
    parser.add_argument("-n", "--number", type=int)

    if len(sys.argv) == 1:
        interactive_menu()
    else:
        args = parser.parse_args()
        if args.menu: interactive_menu()
        else:
            print(Fore.CYAN + "MK_XRAYchecker by mkultra69 with HATE" + Style.RESET_ALL)
            run_logic(args)

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Exit.{Style.RESET_ALL}")
    finally:
        try: shutil.rmtree(TEMP_DIR)
        except: pass


# +═════════════════════════════════════════════════════════════════════════+
# ║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
# ║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
# ║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
# ║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
# ║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
# ║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
# ║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
# ║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
# ║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
# ║                                                                         ║
# +═════════════════════════════════════════════════════════════════════════+
# ║                               by MKultra69                              ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                      https://github.com/MKultra6969                     ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                  mk69.su                                ║
# +═════════════════════════════════════════════════════════════════════════+