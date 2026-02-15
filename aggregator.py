# The original version was taken from https://github.com/y9felix/s

__version__ = "0.10.0"

import urllib.request
import concurrent.futures
import json
import os
import re
import requests
import time
import gzip
import shutil
from rich.progress import track

try:
    import geoip2.database
    HAS_GEOIP_LIB = True
except ImportError:
    HAS_GEOIP_LIB = False
    
def fetch_single_url(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return r.read().decode(errors='ignore').splitlines()
    except Exception:
        return []

def get_flag(code):
    return ''.join(chr(ord(c) + 127397) for c in code.upper()) if code else ''

# --- НАСТРОЙКИ GEOIP ---
# Если поднимете свой сервер (например, https://github.com/ip-api/geoip), впишите сюда его IP
GEOIP_API_URL = "http://ip-api.com/batch?fields=countryCode,query"
MMDB_PATH = "GeoLite2-Country.mmdb"  # Путь к файлу локальной базы

def get_database_country():
    # Используем зеркало, так как github raw часто блокируется или требует VPN
    # Альтернатива: "https://raw.githubusercontent.com/wp-statistics/GeoLite2-Country/master/GeoLite2-Country.mmdb.gz"
    url = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb"
    output_filename = MMDB_PATH  # Используем глобальную переменную

    print(f"[GeoIP] Попытка скачивания базы данных GeoIP...")
    
    try:
        # Обязательно добавляем User-Agent, иначе GitHub может разорвать соединение
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, stream=True, headers=headers, timeout=20)

        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[GeoIP] База успешно скачана: {output_filename}")
            return output_filename
        else:
            print(f"[GeoIP] Ошибка скачивания: статус {response.status_code}")
    except Exception as e:
        print(f"[GeoIP] Критическая ошибка при загрузке базы: {e}")
    return None

# Gemini start
def get_country_batch(ip_list, max_retries=3):
    # 1. ПРИОРИТЕТ: ЛОКАЛЬНАЯ БАЗА (Сверхбыстро, без лимитов)
    if HAS_GEOIP_LIB and os.path.exists(MMDB_PATH):
        results = {}
        try:
            with geoip2.database.Reader(MMDB_PATH) as reader:
                for ip in ip_list:
                    try:
                        response = reader.country(ip)
                        results[ip] = response.country.iso_code or ''
                    except Exception:
                        results[ip] = ''
            return results
        except Exception as e:
            print(f"[GeoIP] Ошибка чтения локальной базы: {e}. Переход на API.")
    
    # 2. ЗАПАСНОЙ ВАРИАНТ: API ЗАПРОСЫ (С защитой от 429 Too Many Requests)
    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(max_retries):
        try:
            data = json.dumps(ip_list)
            # Таймаут побольше, чтобы сервер успел обработать пачку
            response = requests.post(GEOIP_API_URL, data=data, headers=headers, timeout=15)
            
            # Если словили бан по лимитам
            if response.status_code == 429:
                wait_time = int(response.headers.get('X-Ttl', 60)) + 1
                # Если это публичный сервер, лучше сообщить пользователю
                if "ip-api.com" in GEOIP_API_URL:
                    print(f"\n[GeoIP] Лимит API превышен. Ждем разблокировки {wait_time} сек...")
                time.sleep(wait_time)
                continue

            if response.status_code == 200:
                # Умная пауза для публичного API
                if "ip-api.com" in GEOIP_API_URL:
                    remaining = int(response.headers.get('X-Rl', 1))
                    if remaining < 3:
                        time.sleep(2) # Притормозим, если лимиты на исходе
                
                results_json = response.json()
                return {item['query']: item.get('countryCode', '') for item in results_json}

            # Ошибки сервера 5xx
            if 500 <= response.status_code < 600:
                time.sleep(3)
                continue

        except Exception as e:
            # print(f"Ошибка GeoIP API: {e}") # Можно раскомментировать для отладки
            time.sleep(2)
            
    return {}
# Gemini end

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
                cleaned = line.strip()
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
        
        batches = list(range(0, len(ips_to_resolve), batch_size))
        
        if HAS_GEOIP_LIB:
            if not os.path.exists(MMDB_PATH):
                if console: console.print("[yellow]GeoIP база не найдена. Скачивание...[/]")
                get_database_country()
            
            # Повторная проверка, скачалось ли
            if not os.path.exists(MMDB_PATH):
                msg = "[red]Не удалось скачать локальную базу GeoIP. Переход на онлайн API.[/]"
                if console: console.print(msg)
                else: print(msg)
                
        # Если есть локальная база, прогресс-бар пойдет очень быстро
        iterator = track(batches, description="[yellow]GeoIP Resolve...", console=console) if console else batches

        # Проверяем, используем ли мы локальную базу
        using_local_db = HAS_GEOIP_LIB and os.path.exists(MMDB_PATH)

        for i in iterator:
            batch_ips = ips_to_resolve[i:i + batch_size]
            batch_results = get_country_batch(batch_ips)
            
            if batch_results:
                ip_country_map.update(batch_results)
                
                # Если используем API, нужна пауза между пачками
                if not using_local_db:
                    time.sleep(1.6) # 1.6 сек гарант безопасной работы с ip-api (45 req/min)
            else:
                if not using_local_db:
                    time.sleep(2)
            
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