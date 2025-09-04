# داخل bot/main.py بعد استدعاء admin_panel
from aiogram.filters import Command

# عرض كل المفاتيح
@dp.message(Command(commands=["keys"]))
async def keys_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return
    keys = await admin_panel.list_keys()
    if not keys:
        await message.answer("❌ لا توجد مفاتيح مفعلة حالياً.")
        return
    msg = "🔑 قائمة مفاتيح التفعيل:\n"
    for k, active in keys:
        status = "✅ فعال" if active else "❌ معطل"
        msg += f"{k} | {status}\n"
    await message.answer(msg)

# توليد مفتاح جديد
@dp.message(Command(commands=["gen_key"]))
async def gen_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return
    key = await admin_panel.generate_key()
    await message.answer(f"🔑 تم توليد مفتاح جديد:\n{key}")

# تعطيل مفتاح
@dp.message(Command(commands=["deactivate_key"]))
async def deactivate_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ استخدم: /deactivate_key <KEY>")
        return
    key = parts[1]
    await admin_panel.deactivate_key(key)
    await message.answer(f"❌ تم تعطيل المفتاح: {key}")

# تفعيل مفتاح
@dp.message(Command(commands=["activate_key"]))
async def activate_key_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ استخدم: /activate_key <KEY>")
        return
    key = parts[1]
    await admin_panel.activate_key(key)
    await message.answer(f"✅ تم تفعيل المفتاح: {key}")
