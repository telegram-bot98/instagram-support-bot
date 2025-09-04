import random
import string
import asyncio
from bot.db import DB

def generate_key(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

async def main():
    db = DB("data/bot.db")
    await db.init()
    key = generate_key()
    await db.execute("INSERT INTO activation_keys (key, active) VALUES (?,1)", (key,))
    print(f"[✅] مفتاح التفعيل الجديد: {key}")

if __name__ == "__main__":
    asyncio.run(main())
