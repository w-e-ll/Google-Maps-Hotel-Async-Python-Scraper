import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class FHighlights(MainAsyncConn):

    async def create_table_fhighlights(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS fhighlights")
            await conn.execute(
                "CREATE TABLE fhighlights( \
                    fhlid uuid DEFAULT uuid_generate_v4 (), \
                    fhighlight_title TEXT UNIQUE, \
                    PRIMARY KEY(fhlid));")
            print('fhighlights table created')
        finally:
            await conn.close()

    async def create_table_hotel_fhighlight(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_fhighlight")
            await conn.execute(
                "CREATE TABLE hotel_fhighlight( \
                    hotel_id uuid, \
                    fhighlight_id uuid, \
                    PRIMARY KEY (hotel_id, fhighlight_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (fhighlight_id) REFERENCES fhighlights (fhlid) ON DELETE CASCADE);")
            print('hotel_fhighlight table created')
        finally:
            await conn.close()

    async def select_fhighlight(self, fhighlight):
        # Select a row from the table.
        conn = await self.create_conn()
        try:
            fhlid_obj = await conn.fetchrow(
                'SELECT fhlid FROM fhighlights WHERE fhighlight_title = $1;', fhighlight)
            fhlid = str(fhlid_obj['fhlid'])
            return fhlid
        except TypeError as err:
            print(f"No FHLID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_fhighlight(self, fhighlight):
        # Insert fhlid into the highlights table.
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO fhighlights (fhighlight_title) VALUES ($1);'''
            await conn.execute(insert, fhighlight)
        finally:
            await conn.close()

    async def insert_to_hotel_fhighlights_table(self, hid, fhlid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_fhighlight (hotel_id, fhighlight_id) VALUES ($1, $2);''', hid, fhlid)
        finally:
            await conn.close()
