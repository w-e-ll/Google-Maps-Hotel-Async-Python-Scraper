import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Airports(MainAsyncConn):

    async def create_table_nearby_airports(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_airports")
            await conn.execute(
                "CREATE TABLE nearby_airports( \
                    naid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    airport_name TEXT, \
                    airport_distance_car VARCHAR(35), \
                    airport_distance_bus VARCHAR(35), \
                    PRIMARY KEY(naid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_airports table created')
        finally:
            await conn.close()

    async def insert_airport(self, airport_name, airport_distance_car, airport_distance_bus, hid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO nearby_airports (airport_name, airport_distance_car, airport_distance_bus, hotel_id) \
                VALUES ($1, $2, $3, $4);''', airport_name, airport_distance_car, airport_distance_bus, hid)
        finally:
            await conn.close()

    # async def create_table_hotel_nearby_airport(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_nearby_airport")
    #         await conn.execute(
    #             "CREATE TABLE hotel_nearby_airport( \
    #                 hotel_id uuid, \
    #                 nearby_airport_id uuid, \
    #                 PRIMARY KEY (hotel_id, nearby_airport_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (nearby_airport_id) REFERENCES nearby_airports (naid) ON DELETE CASCADE);")
    #         print('hotel_nearby_airport table created')
    #     finally:
    #         await conn.close()

    # async def select_naid(self, airport_name):
    #     conn = await self.create_conn()
    #     try:
    #         naid_obj = await conn.fetchrow(
    #             'SELECT naid FROM nearby_airports WHERE airport_name = $1;', airport_name)
    #         naid = str(naid_obj['naid'])
    #         return naid
    #     finally:
    #         await conn.close()

    # async def insert_to_hotel_nearby_airport_table(self, hid, naid):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute('''
    #             INSERT INTO hotel_nearby_airport (hotel_id, nearby_airport_id) \
    #             VALUES ($1, $2);''', hid, naid)
    #     finally:
    #         await conn.close()
