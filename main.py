import asyncio
from aiogram import Bot, Dispatcher, types
from bot.config import BOT_TOKEN, ADMIN_ID, DB_PATH
from bot.db import DB
from bot.utils import print_banner

async def on_startup(dp):
    print_banner()
    print("[✅] البوت شغال!")

async def handle_start(message: types.Message):
    await message.reply("أهلاً بك! أرسل مفتاح التفعيل لتشغيل البوت.\nمثال: /activate YOUR_KEY")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    
    db = DB(DB_PATH)
    await db.init()
    
    dp.register_message_handler(handle_start, commands=["start"])
    
    await on_startup(dp)
    await dp.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[❌] تم إيقاف البوت يدوياً")
