import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

# تحميل متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

# إنشاء البوت و Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# رسالة ترحيب
WELCOME_TEXT = "مرحبا! أنا بوت استعادة حسابات Instagram."

# مثال handler لأمر /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT)
    if message.from_user.id == ADMIN_ID:
        await message.answer("أهلاً Admin! يمكنك إدارة المفاتيح والمستخدمين.")

# مثال handler لأمر /help
@dp.message(Command(commands=["help"]))
async def help_handler(message: types.Message):
    help_text = """
    /start - تشغيل البوت
    /help - تعليمات
    """
    await message.answer(help_text)

# Main function
async def main():
    print("[✅] البوت شغال...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
