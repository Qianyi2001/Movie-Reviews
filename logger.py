from datetime import datetime

def log_message(level, message):
    print(f"[{level}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
