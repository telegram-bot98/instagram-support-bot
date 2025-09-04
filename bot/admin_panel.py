import aiosqlite
import random
import string

class AdminPanel:
    def __init__(self, db_path):
        self.db = DB(db_path)

    # ---------------------------
    # توليد مفتاح تفعيل جديد
    # ---------------------------
    async def generate_key(self, length=8):
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        await self.db.execute("INSERT INTO activation_keys (key, active) VALUES (?,1)", (key,))
        return key

    # ---------------------------
    # قائمة المفاتيح
    # ---------------------------
    async def list_keys(self):
        keys = await self.db.fetchall("SELECT key, active, assigned_to FROM activation_keys")
        return keys

    # ---------------------------
    # تفعيل مفتاح
    # ---------------------------
    async def activate_key(self, key):
        await self.db.execute("UPDATE activation_keys SET active=1 WHERE key=?", (key,))

    # ---------------------------
    # تعطيل مفتاح
    # ---------------------------
    async def deactivate_key(self, key):
        await self.db.execute("UPDATE activation_keys SET active=0 WHERE key=?", (key,))
