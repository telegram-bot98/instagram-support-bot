import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.db import DB
from bot.worker import Worker

API_TOKEN = "8289211996:AAEW-qfaROZqTpggy1XTeLelbSrwwQbq7VU"
ADMIN_ID = 110484930

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = DB("bot.db")
worker = Worker("bot.db")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = await db.fetchone("SELECT * FROM users WHERE tg_id=?", (message.from_user.id,))
    if not user:
        await db.execute("INSERT INTO users (tg_id, key_used) VALUES (?, ?)", (message.from_user.id, 0))
        await message.answer("👋 أهلاً! أرسل مفتاح التفعيل للبدء.")
    else:
        if user[2] == 1:
            await message.answer("✅ مفتاحك مُفعّل. أرسل يوزر الحساب المبند:")
        else:
            await message.answer("🔑 أرسل مفتاح التفعيل للبدء.")

@dp.message(F.text)
async def check_key(message: Message):
    key = message.text.strip()
    user = await db.fetchone("SELECT * FROM users WHERE tg_id=?", (message.from_user.id,))
    valid_key = await db.fetchone("SELECT * FROM keys WHERE key=? AND used=0", (key,))
    if valid_key:
        await db.execute("UPDATE users SET key_used=1 WHERE tg_id=?", (message.from_user.id,))
        await db.execute("UPDATE keys SET used=1 WHERE key=?", (key,))
        await message.answer("✅ تم تفعيل المفتاح! أرسل يوزر الحساب المبند.")
    else:
        await message.answer("❌ مفتاح غير صالح أو مستخدم من قبل.")

@dp.message(Command("panel"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 غير مسموح!")
    users_count = await db.fetchone("SELECT COUNT(*) FROM users")
    active_accounts = await db.fetchone("SELECT COUNT(*) FROM accounts WHERE status='pending'")
    await message.answer(
        f"📊 لوحة تحكم البوت:\n"
        f"👥 عدد المستخدمين: {users_count[0]}\n"
        f"🔄 الحسابات تحت المعالجة: {active_accounts[0]}"
    )

@dp.message(Command("gen_keys"))
async def generate_keys(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 غير مسموح!")
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("استخدم: /gen_keys 5")
    count = int(parts[1])
    keys = []
    for i in range(count):
        key = f"KEY-{i+1}-{message.message_id}"
        keys.append(key)
        await db.execute("INSERT INTO keys (key, used) VALUES (?, 0)", (key,))
    await message.answer("🔑 المفاتيح الجديدة:\n" + "\n".join(keys))

async def main():
    logging.basicConfig(level=logging.INFO)
    await worker.run(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main
