import aiosqlite

class DB:
    def __init__(self, db_path):
        self.db_path = db_path

    async def execute(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(query, params)
            await conn.commit()

    async def fetchone(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return row

    async def fetchall(self, query, params=()):
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return rows
