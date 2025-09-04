import aiosqlite
import asyncio

class DB:
    def __init__(self, path):
        self.path = path
        self._lock = asyncio.Lock()

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE,
                active INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS activation_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                expires_at TEXT,
                max_accounts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                owner_tg_id INTEGER,
                status TEXT DEFAULT 'pending'
            );
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                url TEXT,
                result TEXT,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """)
            await db.commit()

    async def execute(self, query, params=()):
        async with self._lock:
            async with aiosqlite.connect(self.path) as db:
                cur = await db.execute(query, params)
                await db.commit()
                return cur

    async def fetchall(self, query, params=()):
        async with self._lock:
            async with aiosqlite.connect(self.path) as db:
                cur = await db.execute(query, params)
                rows = await cur.fetchall()
                return rows

    async def fetchone(self, query, params=()):
        async with self._lock:
            async with aiosqlite.connect(self.path) as db:
                cur = await db.execute(query, params)
                row = await cur.fetchone()
                return row
