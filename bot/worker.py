import asyncio
import random
from bot.db import DB
from bot.utils import slow_typing

class Worker:
    def __init__(self, db_path):
        self.db = DB(db_path)

    async def process_account(self, account):
        username = account[1]
        slow_typing(f"[🔄] معالجة الحساب: {username}")
        # محاكاة إرسال طلبات دعم
        urls = await self.db.fetchall("SELECT value FROM settings WHERE key='support_urls'")
        for url in urls:
            slow_typing(f" - إرسال طلب استئناف لـ: {url[0]}")
            await asyncio.sleep(random.randint(2,5))
        # تحديث الحالة بعد المحاولة
        await self.db.execute("UPDATE accounts SET status='done' WHERE id=?", (account[0],))
        slow_typing(f"[✅] انتهت معالجة الحساب: {username}")

    async def run(self):
        accounts = await self.db.fetchall("SELECT * FROM accounts WHERE status='pending'")
        if not accounts:
            slow_typing("[ℹ️] لا توجد حسابات معلقه الآن.")
            return

        for acc in accounts:
            await self.process_account(acc)

# مثال تشغيل
if __name__ == "__main__":
    import os
    db_path = os.getenv("DB_PATH", "data/bot.db")
    worker = Worker(db_path)
    asyncio.run(worker.run())
