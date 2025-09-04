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

# ---------------------------
# /start
# ---------------------------
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT)
    if message.from_user.id == ADMIN_ID:
        await message.answer("أهلاً Admin! يمكنك إدارة المفاتيح والمستخدمين.")

# ---------------------------
# /help
# ---------------------------
@dp.message(Command(commands=["help"]))
async def help_handler(message: types.Message):
    await message.answer("/start - تشغيل البوت\n/help - تعليمات\n/run_worker - معالجة الحسابات (Admin فقط)")

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
# إدارة المفاتيح (Admin)
# ---------------------------
@dp.message(Command(commands=["keys"]))
async def keys_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return
    keys = await admin_panel.list_keys()
    if not keys:
        await message.answer("❌ لا توجد مفاتيح حالياً.")
        return
    msg = "🔑 قائمة مفاتيح التفعيل:\n"
    for k, active, assigned in keys:
        status = "✅ فعال" if active else "❌ معطل"
        msg += f"{k} | {status} | مخصص لـ {assigned if assigned else 'لا أحد'}\n"
    await message.answer(msg)

@dp.message(Command(commands=["gen_key"]))
async def gen_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية.")
        return
    key = await admin_panel.generate_key()
    await message.answer(f"🔑 تم توليد مفتاح جديد:\n{key}")

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

# ---------------------------
# التحقق من مفتاح التفعيل + إضافة يوزر مبند
# ---------------------------
@dp.message()
async def user_message_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # تحقق إذا المستخدم موجود
    user = await admin_panel.db.fetchone("SELECT * FROM users WHERE tg_id=?", (user_id,))
    if not user:
        # افترض الرسالة مفتاح التفعيل
        key = text.upper()
        key_data = await admin_panel.db.fetchone(
            "SELECT key, active, assigned_to FROM activation_keys WHERE key=?", (key,)
        )
        if key_data and key_data[1] == 1:
            if key_data[2] is None:
                # تعيين المفتاح للمستخدم
                await admin_panel.db.execute(
                    "UPDATE activation_keys SET active=0, assigned_to=? WHERE key=?", (user_id, key)
                )
                await admin_panel.db.execute(
                    "INSERT INTO users (tg_id, active, current_request) VALUES (?,1,NULL)", (user_id,)
                )
                await message.answer("✅ تم تفعيل مفتاحك! يمكنك الآن إرسال يوزر واحد فقط للمعالجة.")
            else:
                await message.answer("❌ هذا المفتاح مخصص لمستخدم آخر ولا يمكن استخدامه.")
        else:
            await message.answer("❌ مفتاح غير صالح أو مستخدم من قبل.")
        return

    # المستخدم موجود → تحقق إذا مفعل
    if user[1] == 0:
        await message.answer("❌ مفتاحك غير مفعل أو انتهت صلاحية المفتاح.")
        return

    # منع المستخدم من إرسال أكثر من يوزر بنفس الوقت
    if user[2]:
        await message.answer("⚠️ لديك طلب قيد المعالجة حالياً. انتظر حتى يتم إنهاؤه.")
        return

    # هنا المستخدم جاهز → إضافة الحساب المبند
    username = text.replace('@','')
    existing = await admin_panel.db.fetchone("SELECT * FROM accounts WHERE username=?", (username,))
    if not existing:
        await admin_panel.db.execute(
            "INSERT INTO accounts (username, status) VALUES (?, 'pending')", (username,)
        )
        await admin_panel.db.execute(
            "UPDATE users SET current_request=? WHERE tg_id=?", (username, user_id)
        )
        await message.answer(f"✅ تم إضافة الحساب @{username} للمعالجة.")
    else:
        await message.answer(f"ℹ️ الحساب @{username} موجود مسبقاً في قائمة الانتظار.")

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
