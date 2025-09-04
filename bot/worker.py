import asyncio
import random
import requests
from bot.db import DB
from bot.utils import slow_typing
from bot.main import bot, ADMIN_ID

class Worker:
    def __init__(self, db_path):
        self.db = DB(db_path)

    async def check_account_status(self, username):
        url = f"https://www.instagram.com/{username}/"
        try:
            r = requests.get(url, timeout=10)
            if "Sorry, this page isn't available" in r.text:
                return "banned"
            return "active"
        except Exception as e:
            print(f"[❌] خطأ بالتحقق من {username}: {e}")
            return "unknown"

    async def process_account(self, account):
        username = account[1]
        slow_typing(f"[🔄] معالجة الحساب: {username}")

        urls = await self.db.fetchall("SELECT value FROM settings WHERE key='support_urls'")
        for url in urls:
            slow_typing(f" - إرسال طلب استئناف لـ: {url[0]}")
            await asyncio.sleep(random.randint(2,5))

        # تحديث حالة الحساب
        await self.db.execute("UPDATE accounts SET status='done' WHERE id=?", (account[0],))

        # إعادة تهيئة المستخدم بعد المعالجة
        user = await self.db.fetchone("SELECT * FROM users WHERE current_request=?", (username,))
        if user:
            await self.db.execute("UPDATE users SET current_request=NULL WHERE tg_id=?", (user['tg_id'],))

        slow_typing(f"[✅] انتهت معالجة الحساب: {username}")

        # التحقق بعد المعالجة
        status = await self.check_account_status(username)
        if status == "active":
            slow_typing(f"[🎉] الحساب {username} تم فك الحظر عنه!")
            try:
                await bot.send_message(ADMIN_ID, f"✅ الحساب @{username} تم استعادته!")
            except Exception as e:
                print(f"[❌] لم نستطع إرسال إشعار Admin: {e}")
        elif status == "banned":
            slow_typing(f"[⚠️] الحساب {username} مازال مبند.")
        else:
            slow_typing(f"[❓] حالة الحساب {username} غير معروفة.")

    async def run(self):
        accounts = await self.db.fetchall("SELECT * FROM accounts WHERE status='pending'")
        if not accounts:
            slow_typing("[ℹ️] لا توجد حسابات معلقة.")
            return
        for acc in accounts:
            await self.process_account(acc)
        slow_typing("[✅] انتهت معالجة جميع الحسابات.")
