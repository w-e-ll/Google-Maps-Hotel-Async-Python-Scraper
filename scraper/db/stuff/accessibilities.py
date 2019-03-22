import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Accessibilities(MainAsyncConn):
    async def create_table_accessibilities(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS accessibilities")
            await conn.execute(
                "CREATE TABLE accessibilities( \
                    acid uuid DEFAULT uuid_generate_v4 (), \
                    accessibility_title TEXT UNIQUE, \
                    PRIMARY KEY(acid));")
            print('accessibilities table created')
        finally:
            await conn.close()

    async def create_table_hotel_accessibility(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_accessibility")
            await conn.execute(
                "CREATE TABLE hotel_accessibility( \
                    hotel_id uuid, \
                    accessibility_id uuid, \
                    PRIMARY KEY (hotel_id, accessibility_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (accessibility_id) REFERENCES accessibilities (acid) ON DELETE CASCADE);")
            print('hotel_accessibility table created')
        finally:
            await conn.close()

    async def select_accessibility(self, accessibility):
        conn = await self.create_conn()
        try:
            acid_obj = await conn.fetchrow(
                'SELECT acid FROM accessibilities WHERE accessibility_title = $1;', accessibility)
            acid = str(acid_obj['acid'])
            return acid
        except TypeError as err:
            print(f"No ACID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_accessibility(self, accessibility):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO accessibilities (accessibility_title) VALUES ($1);''', accessibility)
        finally:
            await conn.close()

    async def insert_to_hotel_accessibilities_table(self, hid, acid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_accessibility (hotel_id, accessibility_id) VALUES ($1, $2);''', hid, acid)
        finally:
            await conn.close()
