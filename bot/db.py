import aiosqlite

class DB:
    def __init__(self, path):
        self.path = path

    async def execute(self, query, params=()):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(query, params)
            await db.commit()

    async def fetchone(self, query, params=()):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(query, params)
            result = await cursor.fetchone()
            await cursor.close()
            return result

    async def fetchall(self, query, params=()):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(query, params)
            result = await cursor.fetchall()
            await cursor.close()
            return result
