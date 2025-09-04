import random
import time
from colorama import Fore

def print_banner():
    banner = f"""
{Fore.CYAN}
╔════════════════════════════════════════════════════════════╗
║                Instagram Support Bot Pro                   ║
║         نظام تقديم طلبات الدعم الرسمي لإنستغرام           ║
║                    الإصدار الاحترافي                      ║
╚════════════════════════════════════════════════════════════╝
{Fore.RESET}
    """
    print(banner)

def slow_typing(text, min_delay=0.05, max_delay=0.12):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(random.uniform(min_delay, max_delay))
    print()
