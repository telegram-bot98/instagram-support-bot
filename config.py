import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "data/bot.db")
SPEED_PROFILE = os.getenv("SPEED_PROFILE", "slow")  # slow / medium / fast
USE_PROXIES = os.getenv("USE_PROXIES", "false").lower() in ("1","true","yes")
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS","3"))
