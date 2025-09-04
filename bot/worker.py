import asyncio
import random
import requests
from bot.db import DB
from bot.utils import slow_typing

class Worker:
    def __init__(self, db_path, notify_admin=None):
        self.db = DB(db_path)
        self.notify_admin = notify_admin
        self.descriptions = [
            "أنا أستخدم حسابي بشكل طبيعي ولم أنتهك أي شروط. أرجو إعادة المراجعة.",
            "حسابي شخصي وأستخدمه للتواصل مع الأصدقاء فقط. تم حظري عن طريق الخطأ.",
            "أعتقد أن هناك خطأ أدى إلى حظر حسابي، أرجو المراجعة.",
            "كنت أستخدم التطبيق بشكل طبيعي وفجأة تم حظري، أرجو التدخل.",
            "حسابي مهم للتواصل مع العائلة، أطلب المساعدة في استعادته.",
            "لم أقم بأي نشاط مخالف لشروط الخدمة، أرجو إعادة النظر."
        ]

    async def notify(self, message):
        if self.notify_admin:
            await self.notify_admin(message)

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

    async def send_support_request(self, username, url):
        description = random.choice(self.descriptions)
        slow_typing(f"[🔄] إرسال طلب دعم لـ {username} على الرابط {url} مع وصف: {description}")
        await asyncio.sleep(random.randint(2, 5))  # محاكاة زمن الانتظار للإرسال
        return True

    async def process_account(self, account):
        username = account[1]
        slow_typing(f"[🔄] بدء معالجة الحساب: {username}")

        support_urls = await self.db.fetchall("SELECT value FROM settings WHERE key='support_urls'")
        if not support_urls:
            slow_typing("[⚠️] لا توجد روابط دعم محددة في قاعدة البيانات.")
            return

        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            slow_typing(f"[📊] جولة {attempt} من {max_attempts} لكل رابط دعم")
            for url_tuple in support_urls:
                url = url_tuple[0]
                await self.send_support_request(username, url)

            # تحقق إذا تم فك الباند
            status = await self.check_account_status(username)
            if status == "active":
                slow_typing(f"[🎉] الحساب {username} تم فك الباند عنه!")
                await self.notify(f"✅ الحساب @{username} تم استعادته!")

                await self.db.execute("UPDATE accounts SET status='done' WHERE id=?", (account[0],))
                user = await self.db.fetchone("SELECT * FROM users WHERE current_request=?", (username,))
                if user:
                    await self.db.execute("UPDATE users SET current_request=NULL WHERE tg_id=?", (user['tg_id'],))
                return

            else:
                slow_typing(f"[⚠️] الحساب {username} مازال مبند. متابعة المحاولات...")
                await asyncio.sleep(random.randint(30, 60))

        slow_typing(f"[❌] انتهت جميع المحاولات للحساب {username} ومازال مبند.")
        await self.db.execute("UPDATE accounts SET status='done' WHERE id=?", (account[0],))
        user = await self.db.fetchone("SELECT * FROM users WHERE current_request=?", (username,))
        if user:
            await self.db.execute("UPDATE users SET current_request=NULL WHERE tg_id=?", (user['tg_id'],))

    async def run(self):
        accounts = await self.db.fetchall("SELECT * FROM accounts WHERE status='pending'")
        if not accounts:
            slow_typing("[ℹ️] لا توجد حسابات معلقة.")
            return
        for acc in accounts:
            await self.process_account(acc)
        slow_typing("[✅] انتهت معالجة جميع الحسابات.")
