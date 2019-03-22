import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Things_to_do(MainAsyncConn):

    async def create_table_nearby_things_to_do(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_things_to_do")
            await conn.execute(
                "CREATE TABLE nearby_things_to_do( \
                    nttdid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    thing_name TEXT, \
                    thing_distance_walk VARCHAR(35), \
                    thing_distance_car VARCHAR(35), \
                    thing_distance_bus VARCHAR(35), \
                    thing_img_link TEXT, \
                    PRIMARY KEY(nttdid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_things_to_do table created')
        finally:
            await conn.close()

    async def insert_thing(self, thing_name, thing_distance_walk,
                           thing_distance_car, thing_distance_bus, thing_img_link, hid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO nearby_things_to_do (\
                    thing_name, thing_distance_car, \
                    thing_distance_walk, thing_distance_bus, thing_img_link, hotel_id) \
                VALUES ($1, $2, $3, $4, $5, $6);''', thing_name, thing_distance_car, thing_distance_walk, thing_distance_bus, thing_img_link, hid)
        finally:
            await conn.close()

    # async def create_table_hotel_nearby_thing_to_do(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_nearby_thing_to_do")
    #         await conn.execute(
    #             "CREATE TABLE hotel_nearby_thing_to_do( \
    #                 hotel_id uuid, \
    #                 nearby_thing_to_do_id uuid, \
    #                 PRIMARY KEY (hotel_id, nearby_thing_to_do_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (nearby_thing_to_do_id) REFERENCES nearby_things_to_do (nttdid) ON DELETE CASCADE);")
    #         print('hotel_nearby_thing_to_do table created')
    #     finally:
    #         await conn.close()

    # async def select_nttdid(self, thing_name):
    #     conn = await self.create_conn()
    #     try:
    #         nttdid_obj = await conn.fetchrow(
    #             'SELECT nttdid FROM nearby_things_to_do WHERE thing_name = $1;', str(thing_name))
    #         nttdid = str(nttdid_obj['nttdid'])
    #         return nttdid
    #     except TypeError as err:
    #         print(f"No nttdid: {err}")
    #         pass
    #     finally:
    #         await conn.close()

    # async def insert_to_hotel_nearby_thing_to_do_table(self, hid, nttdid):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute('''
    #             INSERT INTO hotel_nearby_thing_to_do (hotel_id, nearby_thing_to_do_id) \
    #             VALUES ($1, $2);''', hid, nttdid)
    #     finally:
    #         await conn.close()
