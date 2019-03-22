import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class NewHotel(MainAsyncConn):

    async def create_table_hotel(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel")
            await conn.execute(
                "CREATE TABLE hotel( \
                    hid uuid DEFAULT uuid_generate_v4 (), \
                    name TEXT UNIQUE, \
                    phone VARCHAR(35), \
                    address TEXT, \
                    adds BOOLEAN, \
                    website TEXT, \
                    direction TEXT, \
                    description TEXT, \
                    rating VARCHAR(35), \
                    reviews_count VARCHAR(35), \
                    reviews_rating VARCHAR(35), \
                    short_review TEXT, \
                    PRIMARY KEY(hid));")
            print('hotel table created')
        finally:
            await conn.close()

    async def insert_hotel_to_db(self, adds, hname, website, direction, rating, reviews_count,
                                 reviews_rating, address, phone, short_review, description):
        try:
            conn = await self.create_conn()
            insert = '''INSERT INTO hotel( \
                adds, name, website, direction, rating, reviews_count, \
                reviews_rating, address, phone, short_review, description) \
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);'''
            await conn.execute(insert, adds, hname, website, direction, rating, reviews_count,
                               reviews_rating, address, phone, short_review, description)
            print(f'{hname} hotel was added to hotel table')
        finally:
            await conn.close()
