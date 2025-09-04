import sqlite3

conn = sqlite3.connect("bot.db")
c = conn.cursor()

# جدول المستخدمين
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    key_used INTEGER
)
""")

# جدول المفاتيح
c.execute("""
CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT,
    used INTEGER
)
""")

# جدول الحسابات
c.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✅ تم إنشاء الجداول بنجاح")
