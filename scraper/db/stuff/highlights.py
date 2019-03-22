import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Highlights(MainAsyncConn):

    async def create_table_highlights(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS highlights")
            await conn.execute(
                "CREATE TABLE highlights( \
                    hlid uuid DEFAULT uuid_generate_v4 (), \
                    highlight_title TEXT UNIQUE, \
                    highlight_img_url TEXT, \
                    PRIMARY KEY(hlid));")
            print('highlights table created')
        finally:
            await conn.close()

    async def create_table_hotel_highlight(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_highlight")
            await conn.execute(
                "CREATE TABLE hotel_highlight( \
                    hotel_id uuid, \
                    highlight_id uuid, \
                    PRIMARY KEY (hotel_id, highlight_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (highlight_id) REFERENCES highlights (hlid) ON DELETE CASCADE);")
            print('hotel_highlight table created')
        finally:
            await conn.close()

    async def select_highlight(self, highlight_text):
        # Select a row from the table.
        conn = await self.create_conn()
        try:
            hlid_obj = await conn.fetchrow(
                'SELECT hlid FROM highlights WHERE highlight_title = $1;', highlight_text)
            hlid = str(hlid_obj['hlid'])
            return hlid
        except TypeError as err:
            print(f"No HLID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_highlight(self, highlight_img, highlight_text):
        # Insert fid into the facilities table.
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO highlights (highlight_img_url, highlight_title) VALUES ($1, $2);'''
            await conn.execute(insert, highlight_img, highlight_text)
        finally:
            await conn.close()

    async def insert_to_hotel_highlights_table(self, hid, hlid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_highlight (hotel_id, highlight_id) VALUES ($1, $2);''', hid, hlid)
        finally:
            await conn.close()
