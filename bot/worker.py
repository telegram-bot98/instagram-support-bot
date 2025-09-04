import asyncio, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from bot.admin_panel import AdminPanel
from bot.worker import Worker
from bot.db import DB

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_PATH = os.getenv("DB_PATH", "data/bot.db")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

db = DB(DB_PATH)
admin_panel = AdminPanel(DB_PATH)

# ---------------------------
# دالة الإشعار للـ Worker
# ---------------------------
async def notify_admin(message_text):
    try:
        await bot.send_message(ADMIN_ID, message_text)
    except Exception as e:
        print(f"[❌] لم نستطع إرسال إشعار Admin: {e}")

# إنشاء Worker وتمرير دالة الإشعار
worker = Worker(DB_PATH, notify_admin=notify_admin)

WELCOME_TEXT = "مرحبا! أدخل مفتاح التفعيل الخاص بك للمتابعة."

# ---------------------------
# /start
# ---------------------------
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT)

# ---------------------------
# التعامل مع الرسائل (مفتاح أو يوزر)
# ---------------------------
@dp.message()
async def user_message_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    user = await db.fetchone("SELECT * FROM users WHERE tg_id=?", (user_id,))
    if not user:
        key = text.upper()
        key_data = await db.fetchone(
            "SELECT key, active, assigned_to FROM activation_keys WHERE key=?", (key,)
        )
        if key_data and key_data[1] == 1 and key_data[2] is None:
            await db.execute(
                "UPDATE activation_keys SET active=0, assigned_to=? WHERE key=?", (user_id, key)
            )
            await db.execute(
                "INSERT INTO users (tg_id, active, current_request) VALUES (?,1,NULL)", (user_id,)
            )
            await message.answer("✅ تم تفعيل مفتاحك! يمكنك الآن إرسال يوزر واحد فقط للمعالجة.")
        else:
            await message.answer("❌ مفتاح غير صالح أو مستخدم من قبل.")
        return

    if user[1] == 0:
        await message.answer("❌ مفتاحك غير مفعل أو انتهت صلاحيته.")
        return

    if user[2]:
        await message.answer("⚠️ لديك طلب قيد المعالجة حالياً. انتظر حتى يتم إنهاؤه.")
        return

    username = text.replace('@','')
    existing = await db.fetchone("SELECT * FROM accounts WHERE username=?", (username,))
    if not existing:
        await db.execute(
            "INSERT INTO accounts (username, status) VALUES (?, 'pending')", (username,)
        )
        await db.execute(
            "UPDATE users SET current_request=? WHERE tg_id=?", (username, user_id)
        )
        await message.answer(f"✅ تم إضافة الحساب @{username} للمعالجة. البوت سيكرر المحاولات تلقائياً حتى يتم فك الباند.")
    else:
        await message.answer(f"ℹ️ الحساب @{username} موجود مسبقاً في قائمة الانتظار.")

# ---------------------------
# /help
# ---------------------------
@dp.message(Command(commands=["help"]))
async def help_handler(message: types.Message):
    await message.answer("/start - بدء البوت\n/help - تعليمات\n/run_worker - معالجة الحسابات (Admin فقط)")

# ---------------------------
# /run_worker (Admin فقط)
# ---------------------------
@dp.message(Command(commands=["run_worker"]))
async def run_worker_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    await message.answer("🚀 بدء معالجة الحسابات...")
    await worker.run()
    await message.answer("✅ انتهت المعالجة.")

# ---------------------------
# بدء البوت
# ---------------------------
async def main():
    print("[✅] البوت شغال...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
