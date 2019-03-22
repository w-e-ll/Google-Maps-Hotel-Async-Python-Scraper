import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class LocationGettingAround(MainAsyncConn):

    async def create_table_location_getting_around(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_getting_around")
            await conn.execute(
                "CREATE TABLE location_getting_around( \
                    lgaid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_around_name VARCHAR(150), \
                    location_around_type_text TEXT, \
                    PRIMARY KEY(lgaid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_getting_around table created')
        finally:
            await conn.close()

    async def insert_location_getting_around(self, location_around_name,
                                             location_around_type_text, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO location_getting_around ( \
               location_around_name, location_around_type_text, hotel_id) \
                VALUES ($1, $2, $3);'''
            await conn.execute(insert, location_around_name, location_around_type_text, hid)
            print(f'location_getting_around added')
        finally:
            await conn.close()
