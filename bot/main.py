import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage  # المسار الجديد في 3.x
from bot.admin_panel import AdminPanel
from bot.worker import Worker

# تحميل متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

# إنشاء البوت و Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # لا تمرر bot مباشرة

# Initialize Admin Panel and Worker
admin_panel = AdminPanel(DB_PATH)
worker = Worker(DB_PATH)

# رسالة ترحيب
WELCOME_TEXT = "مرحبا! أنا بوت استعادة حسابات Instagram."

# Handler لأمر /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT)
    if message.from_user.id == ADMIN_ID:
        await message.answer("أهلاً Admin! يمكنك إدارة المفاتيح والمستخدمين.")

# Handler لأمر /help
@dp.message(Command(commands=["help"]))
async def help_handler(message: types.Message):
    help_text = """
/start - تشغيل البوت
/help - تعليمات
/run_worker - تشغيل معالجة الحسابات (Admin فقط)
"""
    await message.answer(help_text)

# Handler لأمر /run_worker (Admin فقط)
@dp.message(Command(commands=["run_worker"]))
async def run_worker_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية تشغيل هذا الأمر.")
        return
    await message.answer("🚀 بدء معالجة الحسابات...")
    await worker.run()
    await message.answer("✅ انتهت معالجة الحسابات.")

# Main function
async def main():
    print("[✅] البوت شغال...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
