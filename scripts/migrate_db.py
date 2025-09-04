import asyncio
import aiosqlite

async def migrate():
    async with aiosqlite.connect("bot.db") as db:
        # جدول المستخدمين
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE,
                key_used INTEGER DEFAULT 0,
                current_request TEXT
            )
        """)

        # جدول المفاتيح
        await db.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                used INTEGER DEFAULT 0
            )
        """)

        # جدول الحسابات
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                attempts INTEGER DEFAULT 0
            )
        """)

        await db.commit()
        print("✅ قاعدة البيانات جاهزة!")

asyncio.run(migrate())
