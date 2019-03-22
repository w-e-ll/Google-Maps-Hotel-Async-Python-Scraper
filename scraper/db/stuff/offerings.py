import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Offerings(MainAsyncConn):

    async def create_table_offerings(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS offerings")
            await conn.execute(
                "CREATE TABLE offerings( \
                    ofid uuid DEFAULT uuid_generate_v4 (), \
                    offering_title TEXT UNIQUE, \
                    PRIMARY KEY(ofid));")
            print('offerings table created')
        finally:
            await conn.close()

    async def create_table_hotel_offering(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_offering")
            await conn.execute(
                "CREATE TABLE hotel_offering( \
                    hotel_id uuid, \
                    offering_id uuid, \
                    PRIMARY KEY (hotel_id, offering_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (offering_id) REFERENCES offerings (ofid) ON DELETE CASCADE);")
            print('hotel_offering table created')
        finally:
            await conn.close()

    async def select_offering(self, offering):
        conn = await self.create_conn()
        try:
            ofid_obj = await conn.fetchrow(
                'SELECT ofid FROM offerings WHERE offering_title = $1;', offering)
            ofid = str(ofid_obj['ofid'])
            return ofid
        except TypeError as err:
            print(f"No OFID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_offering(self, offering):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO offerings (offering_title) VALUES ($1);''', offering)
        finally:
            await conn.close()

    async def insert_to_hotel_offerings_table(self, hid, ofid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_offering (hotel_id, offering_id) VALUES ($1, $2);''', hid, ofid)
        finally:
            await conn.close()
