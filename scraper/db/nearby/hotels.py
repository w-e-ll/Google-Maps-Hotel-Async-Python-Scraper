import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Hotels(MainAsyncConn):

    async def create_table_nearby_hotels(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_hotels")
            await conn.execute(
                "CREATE TABLE nearby_hotels( \
                    nhid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    hotel_name TEXT, \
                    hotel_img_link TEXT, \
                    hotel_star_rate VARCHAR(10), \
                    hotel_sum_reviews VARCHAR(10), \
                    hotel_about VARCHAR(50), \
                    hotel_distance VARCHAR(35), \
                    PRIMARY KEY(nhid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_hotels table created')
        finally:
            await conn.close()

    async def insert_nearby_hotel(self, hotel_name, hotel_img_link, hotel_star_rate,
                                  hotel_sum_reviews, hotel_about, hotel_distance, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO nearby_hotels ( \
                            hotel_name, hotel_img_link, hotel_star_rate, \
                            hotel_sum_reviews, hotel_about, hotel_distance, hotel_id) \
                        VALUES ($1, $2, $3, $4, $5, $6, $7);'''
            await conn.execute(insert, hotel_name, hotel_img_link, hotel_star_rate,
                               hotel_sum_reviews, hotel_about, hotel_distance, hid)
        finally:
            await conn.close()

    # async def create_table_hotel_nearby_hotel(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_nearby_hotel")
    #         await conn.execute(
    #             "CREATE TABLE hotel_nearby_hotel( \
    #                 hotel_id uuid, \
    #                 nearby_hotel_id uuid, \
    #                 PRIMARY KEY (hotel_id, nearby_hotel_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (nearby_hotel_id) REFERENCES nearby_hotels (nhid) ON DELETE CASCADE);")
    #         print('hotel_nearby_hotel table created')
    #     finally:
    #         await conn.close()

    # async def select_nhid(self, hotel_name):
    #     conn = await self.create_conn()
    #     try:
    #         nhid_obj = await conn.fetchrow(
    #             'SELECT nhid FROM nearby_hotels WHERE hotel_name = $1;', hotel_name)
    #         nhid = str(naid_obj['nhid'])
    #         return nhid
    #     finally:
    #         await conn.close()

    # async def insert_to_hotel_nearby_hotel_table(self, hid, nhid):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute('''
    #             INSERT INTO hotel_nearby_hotel (hotel_id, nearby_hotel_id) \
    #             VALUES ($1, $2);''', hid, nhid)
    #     finally:
    #         await conn.close()
