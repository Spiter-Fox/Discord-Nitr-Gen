import os
import requests
import threading
import random
import string
import time
from colorama import Fore, init

init(autoreset=True)

LOGO = f"""
{Fore.CYAN}
╭━━━╮╱╱╱╱╭━╮╱╭╮╭╮
╰╮╭╮┃╱╱╱╱┃┃╰╮┃┣╯╰╮
╱┃┃┃┣┳━━╮┃╭╮╰╯┣╮╭╋━┳━━╮
╱┃┃┃┣┫━━┫┃┃╰╮┃┣┫┃┃╭┫╭╮┃
╭╯╰╯┃┣━━┃┃┃╱┃┃┃┃╰┫┃┃╰╯┃
╰━━━┻┻━━╯╰╯╱╰━┻┻━┻╯╰━━╯
{Fore.RESET}
"""

VALID_CODES_FILE = "valid_codes.txt"
THREAD_COUNT = 50
REQUEST_DELAY = 1
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

file_lock = threading.Lock()
print_lock = threading.Lock()

def get_session():
    """Creates a session with a random User-Agent."""
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return session

def generate_advanced_code():
    """Generates a code with a higher chance of valid-like patterns."""
    chars = string.ascii_uppercase + string.digits
    base = ''.join(random.choices(chars, k=14))
    patterns = [
        f"{base[:4]}-{base[4:8]}-{base[8:12]}",
        f"{base[:6]}-{base[6:12]}-{base[12:14]}"
    ]
    return random.choice(patterns)

def check_code(code):
    """Checks if the code is valid using Discord's API."""
    try:
        with get_session() as session:
            response = session.get(
                f"https://discord.com/api/v9/entitlements/gift-codes/{code}",
                params={"with_application": False, "with_subscription_plan": True},
                timeout=15
            )
            time.sleep(REQUEST_DELAY + random.uniform(0, 0.5))
            return response.status_code == 200
    except:
        return False

def worker():
    """Main worker thread function."""
    while True:
        codes = [generate_advanced_code() for _ in range(5)]
        for code in codes:
            for _ in range(2):  # Retry mechanism
                if check_code(code):
                    with file_lock:
                        with open(VALID_CODES_FILE, "a") as f:
                            f.write(f"https://discord.gift/{code}\n")
                    with print_lock:
                        print(Fore.GREEN + f"[!] VALID CODE FOUND: https://discord.gift/{code}")
                    return
                else:
                    with print_lock:
                        print(Fore.RED + f"[X] Invalid: https://discord.gift/{code}")
                time.sleep(5)

def main():
    # Display the logo
    print(LOGO)
    print(f"{Fore.YELLOW}[*] Starting the system...{Fore.RESET}\n")

    # Start the main generation process
    print(f"\n{Fore.MAGENTA}[*] Starting {THREAD_COUNT} threads...{Fore.RESET}")
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    # Keep the main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()