import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Transit_stops(MainAsyncConn):

    async def create_table_nearby_transit_stops(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_transit_stops")
            await conn.execute(
                "CREATE TABLE nearby_transit_stops( \
                    ntsid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    stop_name TEXT, \
                    stop_type VARCHAR(10), \
                    stop_distance VARCHAR(35), \
                    PRIMARY KEY(ntsid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_transit_stops table created')
        finally:
            await conn.close()

    async def insert_transit_stop(self, stop_name, stop_type, stop_distance, hid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO nearby_transit_stops (stop_name, stop_type, stop_distance, hotel_id) \
                VALUES ($1, $2, $3, $4);''', stop_name, stop_type, stop_distance, hid)
        finally:
            await conn.close()

    # async def create_table_hotel_nearby_transit_stop(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_nearby_transit_stop")
    #         await conn.execute(
    #             "CREATE TABLE hotel_nearby_transit_stop( \
    #                 hotel_id uuid, \
    #                 nearby_transit_stop_id uuid, \
    #                 PRIMARY KEY (hotel_id, nearby_transit_stop_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (nearby_transit_stop_id) REFERENCES nearby_transit_stops (ntsid) ON DELETE CASCADE);")
    #         print('hotel_nearby_transit_stop table created')
    #     finally:
    #         await conn.close()

    # async def select_ntsid(self, stop_name):
    #     conn = await self.create_conn()
    #     try:
    #         ntsid_obj = await conn.fetchrow(
    #             'SELECT ntsid FROM nearby_transit_stops WHERE stop_name = $1;', stop_name)
    #         ntsid = str(nttdid_obj['ntsid'])
    #         return ntsid
    #     finally:
    #         await conn.close()

    # async def insert_to_hotel_nearby_transit_stop_table(self, hid, ntsid):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute('''
    #             INSERT INTO hotel_nearby_transit_stop (hotel_id, nearby_transit_stop_id) \
    #             VALUES ($1, $2);''', hid, ntsid)
    #     finally:
    #         await conn.close()
