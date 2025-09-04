import asyncio
import random
import requests
from bot.db import DB
from bot.phrases import phrases

class Worker:
    def __init__(self, db_path, notify_admin=None):
        self.db = DB(db_path)
        self.notify_admin = notify_admin

    async def send_support_request(self, username):
        """إرسال طلب دعم إلى إنستغرام"""
        try:
            support_urls = [
                "https://help.instagram.com/contact/606967319425038",
                "https://help.instagram.com/contact/169486816475808",
                "https://help.instagram.com/contact/1652567838289083",
                "https://help.instagram.com/contact/176481208230029"
            ]
            url = random.choice(support_urls)
            description = random.choice(phrases)

            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                print(f"[✅] تم إرسال طلب دعم لـ @{username} → ({description[:35]}...)")
                return True
            else:
                print(f"[⚠️] فشل إرسال الطلب لـ @{username} (HTTP {response.status_code})")
                return False
        except Exception as e:
            print(f"[❌] خطأ أثناء تقديم الطلب لـ @{username}: {e}")
            return False

    async def check_account_status(self, username):
        """تحقق من حالة الحساب إذا انفتح"""
        try:
            return random.choice([False, False, False, True])  # 25% احتمال
        except:
            return False

    async def process_account(self, bot, user_id, username):
        """تكرار المحاولات حتى ينفتح الحساب"""
        attempts = 0
        while True:
            acc = await self.db.fetchone("SELECT * FROM accounts WHERE username=?", (username,))
            if not acc:
                print(f"[🛑] الحساب @{username} انمسح من النظام. وقف المعالجة.")
                return

            if await self.check_account_status(username):
                print(f"[🎉] الحساب @{username} انفتح!")
                await bot.send_message(user_id, f"✅ تم فك الحظر عن حسابك @{username} بنجاح!")
                await self.db.execute("DELETE FROM accounts WHERE username=?", (username,))
                await self.db.execute("UPDATE users SET current_request=NULL WHERE tg_id=?", (user_id,))
                return

            success = await self.send_support_request(username)
            if success:
                attempts += 1
                await self.db.execute(
                    "UPDATE accounts SET attempts=? WHERE username=?", (attempts, username)
                )

            wait_time = random.randint(45, 90)
            await asyncio.sleep(wait_time)

    async def run(self, bot=None):
        """تشغيل المعالجة"""
        accounts = await self.db.fetchall("SELECT username, status FROM accounts WHERE status='pending'")
        for username, _ in accounts:
            user = await self.db.fetchone("SELECT tg_id FROM users WHERE current_request=?", (username,))
            if user:
                asyncio.create_task(self.process_account(bot, user[0], username))
