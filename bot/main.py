import asyncio, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from bot.admin_panel import AdminPanel
from bot.worker import Worker

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

admin_panel = AdminPanel(DB_PATH)
worker = Worker(DB_PATH)

WELCOME_TEXT = "مرحبا! أنا بوت استعادة حسابات Instagram."

# /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT)
    if message.from_user.id == ADMIN_ID:
        await message.answer("أهلاً Admin! يمكنك إدارة المفاتيح والمستخدمين.")

# /help
@dp.message(Command(commands=["help"]))
async def help_handler(message: types.Message):
    await message.answer("/start - تشغيل البوت\n/help - تعليمات\n/run_worker - معالجة الحسابات (Admin فقط)")

# /run_worker
@dp.message(Command(commands=["run_worker"]))
async def run_worker_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    await message.answer("🚀 بدء معالجة الحسابات...")
    await worker.run()
    await message.answer("✅ انتهت المعالجة.")

# /keys
@dp.message(Command(commands=["keys"]))
async def keys_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    keys = await admin_panel.list_keys()
    if not keys:
        await message.answer("❌ لا توجد مفاتيح حالياً.")
        return
    msg = "🔑 قائمة مفاتيح التفعيل:\n"
    for k, active in keys:
        status = "✅ فعال" if active else "❌ معطل"
        msg += f"{k} | {status}\n"
    await message.answer(msg)

# /gen_key
@dp.message(Command(commands=["gen_key"]))
async def gen_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    key = await admin_panel.generate_key()
    await message.answer(f"🔑 تم توليد مفتاح جديد:\n{key}")

# /deactivate_key <KEY>
@dp.message(Command(commands=["deactivate_key"]))
async def deactivate_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ استخدم: /deactivate_key <KEY>")
        return
    key = parts[1]
    await admin_panel.deactivate_key(key)
    await message.answer(f"❌ تم تعطيل المفتاح: {key}")

# /activate_key <KEY>
@dp.message(Command(commands=["activate_key"]))
async def activate_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ استخدم: /activate_key <KEY>")
        return
    key = parts[1]
    await admin_panel.activate_key(key)
    await message.answer(f"✅ تم تفعيل المفتاح: {key}")

async def main():
    print("[✅] البوت شغال...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
