import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Crowds(MainAsyncConn):

    async def create_table_crowds(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS crowds")
            await conn.execute(
                "CREATE TABLE crowds( \
                    crid uuid DEFAULT uuid_generate_v4 (), \
                    crowd_title TEXT UNIQUE, \
                    PRIMARY KEY(crid));")
            print('crowds table created')
        finally:
            await conn.close()

    async def create_table_hotel_crowd(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_crowd")
            await conn.execute(
                "CREATE TABLE hotel_crowd( \
                    hotel_id uuid, \
                    crowd_id uuid, \
                    PRIMARY KEY (hotel_id, crowd_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (crowd_id) REFERENCES crowds (crid) ON DELETE CASCADE);")
            print('hotel_crowd table created')
        finally:
            await conn.close()

    async def select_crowd(self, crowd):
        conn = await self.create_conn()
        try:
            crid_obj = await conn.fetchrow(
                'SELECT crid FROM crowds WHERE crowd_title = $1;', crowd)
            crid = str(crid_obj['crid'])
            return crid
        except TypeError as err:
            print(f"No CRID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_crowd(self, crowd):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO crowds (crowd_title) VALUES ($1);''', crowd)
        finally:
            await conn.close()

    async def insert_to_hotel_crowds_table(self, hid, crid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_crowd (hotel_id, crowd_id) VALUES ($1, $2);''', hid, crid)
        finally:
            await conn.close()
