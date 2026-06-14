import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'dry_run.log')

def log(phone: str, message: str, status: str):
    entry = f"[{datetime.now().isoformat()}] {status} | {phone} | {message}"
    print(entry)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')