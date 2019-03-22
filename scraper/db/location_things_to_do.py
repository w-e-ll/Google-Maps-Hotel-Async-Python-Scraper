import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class LocationThingsToDo(MainAsyncConn):

    async def create_table_location_things_to_do(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_things_to_do")
            await conn.execute(
                "CREATE TABLE location_things_to_do( \
                    lttdid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_thing_name VARCHAR(100), \
                    location_thing_text TEXT, \
                    location_thing_review_rate VARCHAR(20), \
                    location_thing_star_score VARCHAR(10), \
                    location_thing_distance VARCHAR(100), \
                    location_thing_img TEXT, \
                    PRIMARY KEY(lttdid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_score table created')
        finally:
            await conn.close()

    async def insert_location_thing_to_do(self, location_thing_name, location_thing_text,
                                          location_thing_review_rate, location_thing_star_score,
                                          location_thing_distance, location_thing_img, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO location_things_to_do ( \
               location_thing_name, location_thing_text, \
               location_thing_review_rate, location_thing_star_score, \
               location_thing_distance, location_thing_img, hotel_id) \
                VALUES ($1, $2, $3, $4, $5, $6, $7);'''
            await conn.execute(insert, location_thing_name, location_thing_text,
                               location_thing_review_rate, location_thing_star_score,
                               location_thing_distance, location_thing_img, hid)
            print(f'location_score added')
        finally:
            await conn.close()
