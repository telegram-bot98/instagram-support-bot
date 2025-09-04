import asyncio, os
from bot.db import DB

async def main():
    db_path = os.getenv("DB_PATH", "data/bot.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = DB(db_path)
    await db.init()
    await db.execute("""CREATE TABLE IF NOT EXISTS users (tg_id INTEGER PRIMARY KEY, active INTEGER DEFAULT 0)""")
    await db.execute("""CREATE TABLE IF NOT EXISTS activation_keys (key TEXT PRIMARY KEY, active INTEGER DEFAULT 1)""")
    await db.execute("""CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, status TEXT DEFAULT 'pending')""")
    await db.execute("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
    print("[✅] قاعدة البيانات جاهزة!")

if __name__ == "__main__":
    asyncio.run(main())
