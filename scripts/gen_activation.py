import asyncio, random, string
from bot.db import DB
import os

async def main():
    db_path = os.getenv("DB_PATH", "data/bot.db")
    db = DB(db_path)
    for _ in range(5):
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        await db.execute("INSERT OR IGNORE INTO activation_keys (key, active) VALUES (?,1)", (key,))
        print(f"🔑 مفتاح جديد: {key}")

if __name__ == "__main__":
    asyncio.run(main())
