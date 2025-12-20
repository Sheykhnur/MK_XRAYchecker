from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone
import time
import random
import logging
import os

# -----------------
version = "1.0"
log_id = -1003669488656
token="" #вставьте токен!!!
link_subs="https://etoneya.a9fm.site/1"
args="--timeout 10 --threads 2"
sleep_time=500
# sleep_time=30
# -----------------

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO
)

while True:
    os.system(f"python3 v2rayChecker.py -u {link_subs} {args}")
    namefile = f"result_{datetime.now(timezone.utc)}"
    os.rename("sortedProxy.txt", namefile)
    app = Client("bot", api_id=2860432, api_hash="2fde6ca0f8ae7bb58844457a239c7214", bot_token=token)
    with app:
        app.send_document(log_id, document=namefile, caption=f"С аргументами: {args.replace('--', "-")}\nТеперь спать на {sleep_time}сек")
    os.remove(namefile)

    print(f"Сон {sleep_time} секунд")
    time.sleep(sleep_time)
