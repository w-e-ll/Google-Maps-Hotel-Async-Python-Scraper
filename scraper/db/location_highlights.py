import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class LocationHighlights(MainAsyncConn):

    async def create_table_location_overview(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_overview")
            await conn.execute(
                "CREATE TABLE location_overview( \
                    lovid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_overview_text TEXT, \
                    PRIMARY KEY(lovid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_overview table created')
        finally:
            await conn.close()

    async def insert_location_overview(self, location_overview_text, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO location_overview ( \
                location_overview_text, hotel_id) \
                VALUES ($1, $2);'''
            await conn.execute(insert, location_overview_text, hid)
            print(f'location_overview_text added')
        finally:
            await conn.close()

    async def create_table_location_score(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_score")
            await conn.execute(
                "CREATE TABLE location_score( \
                    losid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    score_rate VARCHAR(15), \
                    score_text TEXT, \
                    PRIMARY KEY(losid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_score table created')
        finally:
            await conn.close()

    async def insert_location_score(self, score_rate, score_text, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO location_score ( \
               score_rate, score_text, hotel_id) \
                VALUES ($1, $2, $3);'''
            await conn.execute(insert, score_rate, score_text, hid)
            print(f'location_score added')
        finally:
            await conn.close()
