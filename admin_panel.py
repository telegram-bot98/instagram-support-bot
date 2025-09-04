import asyncio
from bot.db import DB

class AdminPanel:
    def __init__(self, db_path):
        self.db = DB(db_path)

    async def list_users(self):
        users = await self.db.fetchall("SELECT tg_id, active FROM users")
        print("[📋] قائمة المستخدمين:")
        for u in users:
            print(f" - {u[0]} | Active: {u[1]}")

    async def list_activation_keys(self):
        keys = await self.db.fetchall("SELECT key, active FROM activation_keys")
        print("[🔑] قائمة مفاتيح التفعيل:")
        for k in keys:
            print(f" - {k[0]} | Active: {k[1]}")

    async def activate_user(self, tg_id):
        await self.db.execute("UPDATE users SET active=1 WHERE tg_id=?", (tg_id,))
        print(f"[✅] تم تفعيل المستخدم: {tg_id}")

    async def deactivate_user(self, tg_id):
        await self.db.execute("UPDATE users SET active=0 WHERE tg_id=?", (tg_id,))
        print(f"[⚠️] تم تعطيل المستخدم: {tg_id}")

    async def deactivate_key(self, key):
        await self.db.execute("UPDATE activation_keys SET active=0 WHERE key=?", (key,))
        print(f"[⚠️] تم تعطيل مفتاح التفعيل: {key}")


# مثال تشغيل
if __name__ == "__main__":
    import os
    db_path = os.getenv("DB_PATH", "data/bot.db")
    panel = AdminPanel(db_path)
    asyncio.run(panel.list_users())
    asyncio.run(panel.list_activation_keys())
