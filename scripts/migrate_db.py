import asyncio
import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "data/bot.db")

async def migrate():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS activation_keys (
            key TEXT PRIMARY KEY,
            active INTEGER DEFAULT 1,
            assigned_to INTEGER
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            active INTEGER DEFAULT 0,
            current_request TEXT DEFAULT NULL
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            status TEXT DEFAULT 'pending'
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)
        await conn.commit()
    print("[✅] تم إنشاء الجداول بنجاح!")

if __name__ == "__main__":
    asyncio.run(migrate())
