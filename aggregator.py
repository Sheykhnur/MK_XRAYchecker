# The original version was taken from https://github.com/y9felix/s

__version__ = "0.9.0"

import urllib.request
import concurrent.futures
import json
import os
import re
import requests
import time
from rich.progress import track

def fetch_single_url(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode(errors='ignore').splitlines()
    except Exception:
        return []

def get_flag(code):
    return ''.join(chr(ord(c) + 127397) for c in code.upper()) if code else ''

def get_country_batch(ip_list):
    url = "http://ip-api.com/batch?fields=countryCode,query"
    try:
        data = json.dumps(ip_list)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json()
            return {item['query']: item.get('countryCode', '') for item in results}
    except Exception as e:
        print(f"Ошибка GeoIP API: {e}")
    return {}

def get_aggregated_links(url_map, selected_categories, keywords, use_old=False, log_func=print, console=None):
    urls = []
    old_lines = set()
    unique_configs = set()
    
    PROTOCOL_PATTERN = re.compile(r'^(vless|vmess|trojan|ss|hysteria2|hy2)://', re.IGNORECASE)
    IP_EXTRACT_PATTERN = re.compile(r'@([^:]+):')

    if use_old and os.path.exists('old.json'):
        try:
            with open('old.json', 'r') as f:
                old_lines = set(json.load(f))
        except: pass

    for cat in selected_categories:
        sources = url_map.get(cat, [])
        if isinstance(sources, list):
            urls.extend(sources)
        elif isinstance(sources, str):
            urls.extend(sources.split())

    if console:
        console.print(f"[bold cyan]АГРЕГАТОР:[/] Загрузка из {len(urls)} источников...")
    else:
        log_func(f"АГРЕГАТОР: Загрузка из {len(urls)} источников...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = list(executor.map(fetch_single_url, urls))
        
        iterator = track(futures, description="[green]Скачивание источников...", console=console) if console else futures
        
        for result in iterator:
            for line in result:
                cleaned = line.split('#')[0].strip()
                if not cleaned: continue
                if not PROTOCOL_PATTERN.match(cleaned): continue
                is_valid = True
                if keywords:
                    is_valid = any(word.lower() in line.lower() for word in keywords)
                if is_valid and cleaned not in old_lines:
                    unique_configs.add(cleaned)

    config_list = list(unique_configs)
    total_configs = len(config_list)

    if total_configs > 0:
        if console:
            console.print(f"[bold cyan]АГРЕГАТОР:[/] Найдено {total_configs} конфигов. Определение стран...")
        else:
            log_func(f"АГРЕГАТОР: Найдено {total_configs} конфигов. Определение стран...")
        
        ips_to_resolve = []
        for line in config_list:
            match = IP_EXTRACT_PATTERN.search(line)
            if match:
                ips_to_resolve.append(match.group(1))
        
        ips_to_resolve = list(set(ips_to_resolve))
        ip_country_map = {}
        batch_size = 100
        
        batches = range(0, len(ips_to_resolve), batch_size)
        if console:
            batches = track(batches, description="[yellow]GeoIP Resolve...", console=console)

        consecutive_errors = 0
        for i in batches:
            if consecutive_errors >= 5:
                msg = "[yellow]GeoIP API недоступен (слишком много запросов). Пропуск остальных IP...[/]"
                if console: console.print(msg)
                else: log_func(msg)
                break

            batch_ips = ips_to_resolve[i:i + batch_size]
            batch_results = get_country_batch(batch_ips)
            
            if batch_results:
                ip_country_map.update(batch_results)
                consecutive_errors = 0
                time.sleep(1.3)
            else:
                consecutive_errors += 1
                time.sleep(3)
            
        final_lines = []
        for line in config_list:
            match = IP_EXTRACT_PATTERN.search(line)
            ip = match.group(1) if match else ''
            country_code = ip_country_map.get(ip, '')
            flag = get_flag(country_code)
            if flag:
                final_lines.append(f"{line} {flag}" if '#' in line else f"{line}#{flag}")
            else:
                final_lines.append(line)
                
        msg = f"АГРЕГАТОР: Собрано {len(final_lines)} новых уникальных конфигураций."
        if console: console.print(f"[bold green]{msg}[/]")
        else: log_func(msg)
        
        return final_lines

    if console: console.print("[red]АГРЕГАТОР: Ничего нового не найдено.[/]")
    else: log_func("АГРЕГАТОР: Ничего нового не найдено.")
    return []

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