import asyncio
from bot.db import DB

async def main():
    db = DB("data/bot.db")
    await db.init()
    print("[✅] قاعدة البيانات جاهزة!")

if __name__ == "__main__":
    asyncio.run(main())
