import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class MappedUrls(MainAsyncConn):

    async def create_table_mapped_urls(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS mapped_urls")
            await conn.execute(
                "CREATE TABLE mapped_urls( \
                    uid uuid DEFAULT uuid_generate_v4 (), \
                    url TEXT, \
                    PRIMARY KEY(uid));")
            print('mapped_urls table created')
        finally:
            await conn.close()

    async def create_table_hotel_mapped_url(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_mapped_url")
            await conn.execute(
                "CREATE TABLE hotel_mapped_urls( \
                    hotel_id uuid, \
                    url_id uuid, \
                    PRIMARY KEY (hotel_id, url_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (url_id) REFERENCES mapped_urls (uid) ON DELETE CASCADE);")
            print('hotel_mapped_url table created')
        finally:
            await conn.close()

    async def select_url(self, mapped_url):
        conn = await self.create_conn()
        try:
            uid_obj = await conn.fetchrow(
                'SELECT uid FROM mapped_urls WHERE url = $1;', mapped_url)
            uid = str(uid_obj['uid'])
            return uid
        except TypeError as err:
            print(f"No UID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_url(self, mapped_url):
        conn = await self.create_conn()
        try:
            insert = "INSERT INTO mapped_urls (url) VALUES ($1);"
            await conn.execute(insert, mapped_url)
        finally:
            await conn.close()

    async def insert_to_hotel_mapped_url(self, hid, uid):
        conn = await self.create_conn()
        try:
            insert = "INSERT INTO hotel_mapped_urls (hotel_id, url_id) VALUES ($1, $2);"
            await conn.execute(insert, hid, uid)
        finally:
            await conn.close()
