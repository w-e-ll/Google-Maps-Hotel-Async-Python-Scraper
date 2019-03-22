import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Amenities(MainAsyncConn):

    async def create_table_amenities(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS amenities")
            await conn.execute(
                "CREATE TABLE amenities( \
                    aid uuid DEFAULT uuid_generate_v4 (), \
                    amenity_title TEXT UNIQUE, \
                    PRIMARY KEY(aid));")
            print('amenities table created')
        finally:
            await conn.close()

    async def create_table_hotel_amenity(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_amenity")
            await conn.execute(
                "CREATE TABLE hotel_amenity( \
                    hotel_id uuid, \
                    amenity_id uuid, \
                    PRIMARY KEY (hotel_id, amenity_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (amenity_id) REFERENCES amenities (aid) ON DELETE CASCADE);")
            print('hotel_amenity table created')
        finally:
            await conn.close()

    async def select_amenity(self, amenity):
        # Select a row from the table.
        conn = await self.create_conn()
        try:
            aid_obj = await conn.fetchrow(
                'SELECT aid FROM amenities WHERE amenity_title = $1;', amenity)
            aid = str(aid_obj['aid'])
            return aid
        except TypeError as err:
            print(f"No AID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_amenity(self, amenity):
        # Insert fid into the facilities table.
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO amenities (amenity_title) VALUES ($1);''', amenity)
        finally:
            await conn.close()

    async def insert_to_hotel_amenities_table(self, hid, aid):
        # insert_to_hotel_amenities_table
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_amenity (hotel_id, amenity_id) VALUES ($1, $2);''', hid, aid)
        finally:
            await conn.close()
