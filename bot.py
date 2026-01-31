from pyrogram import Client
from datetime import datetime, timezone
import time
import os
import sys
import platform
import urllib.request
import zipfile
import shutil
import logging
import json

version = "1.2.2"
links = [
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/died",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/archived",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/test",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/1",
    # igareck
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    # lowik
    "https://raw.githubusercontent.com/LowiKLive/BypassWhitelistRu/refs/heads/main/WhiteList-Bypass_Ru.txt",
    # yzewe
    "https://vpn.yzewe.ru/7145117452/K8F8xYDVIcFWauMEi7Q77w",
    # livpn
    "https://livpn.webspot.sbs/sub.php?token=5daff2b2a10a65d50798efb4a2e57533",
    # kort0881
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/subscriptions/all.txt",
    # v2ray-public
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha-All-Type.txt",
    # goida
    "https://github.com/AvenCores/goida-vpn-configs/raw/refs/heads/main/githubmirror/26.txt",
    # zieng2
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt",
    # y9felix
    "http://github.com/y9felix/s/raw/main/b#best",
    # bpwlfree
    "https://bp.wl.free.nf/confs/merged.txt",
    # lime
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt",
    "https://raw.githubusercontent.com/xcom024/vless/refs/heads/main/list.txt",
    "https://github.com/KiryaScript/white-lists/raw/refs/heads/main/githubmirror/28.txt",
    "https://github.com/KiryaScript/white-lists/raw/refs/heads/main/githubmirror/27.txt",
    "https://github.com/KiryaScript/white-lists/raw/refs/heads/main/githubmirror/26.txt",
    "https://wlr.s3-website.cloud.ru/zNhbYZtBc",
    "https://s3c3.001.gpucloud.ru/dixsm/htxml",
    "https://raw.githubusercontent.com/sakha1370/OpenRay/refs/heads/main/output/kind/vless.txt",
    "https://raw.githubusercontent.com/FLEXIY0/matryoshka-vpn/main/configs/russia_whitelist.txt",
    "https://storage.yandexcloud.net/cid-vpn/whitelist.txt",
    "http://fsub.flux.2bd.net/githubmirror/bypass/bypass-all.txt",
    "https://storage.yandexcloud.net/nllrcn-proxy-subs/subs/main-sub.txt",
    "https://raw.githubusercontent.com/whoahaow/rjsxrd/refs/heads/main/githubmirror/bypass-unsecure/bypass-unsecure-all.txt",
    "https://raw.githubusercontent.com/vsevjik/OBSpiskov/refs/heads/main/wwh#OBSpiskov",
    "https://raw.githubusercontent.com/STR97/STRUGOV/refs/heads/main/STR.BYPASS#STR.BYPAS  S👾",
    "https://bp.wl.free.nf/confs/wl.txt",
    "https://bp.wl.free.nf/confs/selected.txt",
    "https://nowmeow.pw/8ybBd3fdCAQ6Ew5H0d66Y1hMbh63GpKUtEXQClIu/whitelist",
    "https://rstnnl.gitverse.site/sb/dev.txt",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/whitelist",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt",
    "https://raw.githubusercontent.com/55prosek-lgtm/vpn_config_for_russia/refs/heads/main/whitelist.txt",
    "https://raw.githubusercontent.com/Created-By/Telegram-Eag1e_YT/main/%40Eag1e_YT",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/Clash_T  ,H",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/T  ,H",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/Clash_Reality",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/Reality",
    "https://peige.dpkj.qzz.io/dapei",
    "https://raw.githubusercontent.com/ovmvo/SubShare/refs/heads/main/sub/permanent/mihomo.yaml",
    "https://raw.githubusercontent.com/AzadNetCH/Clash/main/AzadNet_hy.txt",
    "https://raw.githubusercontent.com/amirkma/proxykma/refs/heads/main/mix.txt",
    "https://world79.spcs.bio/redirect/?Link_id=1125164&redirect=https%3A%2F%2Fraw.githubusercontent.com%2Fmahdibland%2FV2RayAggregator%2Fmaster%2FEternity&sid=",
    "https://4pda.to/stat/go?u=https%3A%2F%2Fgist.githubusercontent.com%2FSyavar%2F7b868a1682aa4a87d9ec2e9bca729f38%2Fraw%2F75ff3ee7c1bb9e08c5f1d91cbc4ee2b82d25635a%2Fgistfile1.txt&e=140404680",
    "https://gist.githubusercontent.com/Syavar/3e76222fc05fde9abcb35c2f24572021/raw/e2f7ef901ae4ba5bab7bef20adef41bead7ba626/gistfile1.txt",
    "https://raw.githubusercontent.com/Kirillo4ka/vpn-configs-for-russia/refs/heads/main/Vless-Rus-Mobile-White-List.txt",
    "https://raw.githubusercontent.com/vlesscollector/vlesscollector/refs/heads/main/vless_configs.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vless.txt",
    "https://github.com/jagger235711/V2rayCollector/blob/main/results/hysteria2.txt",
    "https://raw.githubusercontent.com/hamedp-71/v2go_NEW/main/All_Configs_base64_Sub.txt",
    "https://raw.githubusercontent.com/hamedp-71/v2go_NEW/main/Splitted-By-Protocol/hy2.txt",
    "https://raw.githubusercontent.com/ninjastrikers/v2ray-configs/main/splitted/vless.txt",
    "https://github.com/kismetpro/NodeSuber/raw/refs/heads/main/out/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Sage-77/V2ray-configs/main/config.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-key-vless/refs/heads/main/vpn-files/all_posts.txt",
    "https://raw.githubusercontent.com/SoroushImanian/BlackKnight/main/sub/vlessbase64",
    "https://github.com/kismetpro/NodeSuber/raw/refs/heads/main/Splitted-By-Protocol/vless.txt",
    "https://github.com/kismetpro/NodeSuber/raw/refs/heads/main/Splitted-By-Protocol/trojan.txt",
]

args = "--timeout 10 --t2kill 5"
sleep_time = 500

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO
)

def get_bot_config():
    config_file = "bot.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        log_id = int(input("Введите ваш id (получить можно в @Getmyid_Work_Bot):"))
        token = str(input("Введите токен бота (получить можно в @BotFather):"))
        config = {"log_id": log_id, "token": token}
        with open(config_file, 'w') as f:
            json.dump(config, f)
        return config

config = get_bot_config()
log_id = config["log_id"]
token = config["token"]


app = Client("bot", api_id=2860432, api_hash="2fde6ca0f8ae7bb58844457a239c7214", bot_token=token)
with app:
    app.send_message(log_id, "Бот запущен! Качаю зависимости, и начинаю работу")

if platform.system() == "Windows":
    XRAY_PATH = os.path.join("bin", "xray.exe")
else:
    XRAY_PATH = os.path.join("bin", "xray")

os.makedirs("bin", exist_ok=True)

def get_arch():
    machine = platform.machine().lower()
    if machine in ("i386", "i686"):
        return "32"
    elif machine in ("x86_64", "amd64"):
        return "64"
    elif "armv5" in machine:
        return "arm32-v5"
    elif "armv6" in machine:
        return "arm32-v6"
    elif machine in ("armv7l", "armv7"):
        return "arm32-v7a"
    elif machine in ("aarch64", "arm64"):
        return "arm64-v8a"
    elif "riscv64" in machine:
        return "riscv64"
    elif "ppc64le" in machine:
        return "ppc64le"
    elif "ppc64" in machine:
        return "ppc64"
    elif "s390x" in machine:
        return "s390x"
    else:
        raise OSError(f"Unsupported architecture: {machine}")

def download_xray():
    arch = get_arch()
    url = f"https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-{arch}.zip"
    if platform.system() == "Windows":
        url = f"https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-{arch}.zip"

    logging.info(f"Downloading Xray for {arch} from {url}")
    try:
        zip_path = os.path.join("bin", "xray_temp.zip")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            binary_name = "xray.exe" if platform.system() == "Windows" else "xray"
            zf.extract(binary_name, "bin")
            os.chmod(os.path.join("bin", binary_name), 0o755)

        os.remove(zip_path)
        logging.info("Xray installed successfully.")
    except Exception as e:
        logging.error(f"Failed to download or extract Xray: {e}")
        raise RuntimeError("Xray installation failed") from e

if not os.path.isfile(XRAY_PATH):
    logging.warning("Xray binary not found. Downloading...")
    download_xray()

try:
    import subprocess
    result = subprocess.run([XRAY_PATH, "-version"], capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError("Xray binary is not working")
    logging.info(f"Xray version: {result.stdout.strip()}")
except Exception as e:
    logging.error(f"Xray verification failed: {e}")
    sys.exit(1)

# start script
try:
    if platform.system() == "Windows":
        python_var = "python"
    else:
        python_var = "python3"

    for i in links:
        try:
            os.system(f"{python_var} v2rayChecker.py -u {i} {args}")
            namefile = f"result_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            os.rename("sortedProxy.txt", namefile)

            app = Client("bot", api_id=2860432, api_hash="2fde6ca0f8ae7bb58844457a239c7214", bot_token=token)
            with app:
                app.send_document(log_id, document=namefile, caption=f"{i}\nС аргументами: {args.replace('--', '-')}\nТеперь спать на {sleep_time}сек")
            os.remove(namefile)
        except:
            pass

    logging.info(f"Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)

except Exception as e:
    logging.exception("Unexpected error in main loop")
    time.sleep(60)
