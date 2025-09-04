import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.db import DB
from bot.worker import Worker
import os

# قراءة التوكن و ADMIN_ID من environment
API_TOKEN = os.getenv("BOT_TOKEN", "8289211996:AAEW-qfaROZqTpggy1XTeLelbSrwwQbq7VU")
ADMIN_ID = int(os.getenv("ADMIN_ID", "110484930"))

# مسار قاعدة البيانات
DB_PATH = os.getenv("DB_PATH", "bot.db")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = DB(DB_PATH)
worker = Worker(DB_PATH)

# --- أوامر البوت ---

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

# أمر Debug لمعرفة الـ ID
@dp.message(Command("whoami"))
async def whoami(message: Message):
    await message.answer(
        f"📌 ID اللي البوت شايفه هو: {message.from_user.id}\n"
        f"📌 ADMIN_ID بالكود هو: {ADMIN_ID}"
    )

# أمر /help للأدمن فقط
@dp.message(Command("help"))
async def help_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("🚫 غير مسموح!")
    
    commands = [
        "/start - بدء المحادثة مع البوت",
        "/gen_keys <عدد> - توليد مفاتيح جديدة",
        "/panel - عرض لوحة تحكم البوت",
        "/whoami - معرفة ID مالك الحساب والـ ADMIN_ID",
        "/help - عرض كل أوامر الأدمن"
    ]
    
    await message.answer("📜 أوامر البوت للـ admin:\n\n" + "\n".join(commands))

# --- Main ---
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # شغّل worker في الخلفية
    asyncio.create_task(worker.run(bot))
    
    # شغّل polling للبوت
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
