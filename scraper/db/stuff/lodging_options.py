import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Lodging_options(MainAsyncConn):

    async def create_table_lodging_options(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS lodging_options")
            await conn.execute(
                "CREATE TABLE lodging_options( \
                    loid uuid DEFAULT uuid_generate_v4 (), \
                    lodging_option_title TEXT UNIQUE, \
                    PRIMARY KEY(loid));")
            print('lodging_option table created')
        finally:
            await conn.close()

    async def create_table_hotel_lodging_option(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_lodging_option")
            await conn.execute(
                "CREATE TABLE hotel_lodging_option( \
                    hotel_id uuid, \
                    lodging_option_id uuid, \
                    PRIMARY KEY (hotel_id, lodging_option_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (lodging_option_id) REFERENCES lodging_options (loid) ON DELETE CASCADE);")
            print('hotel_lodging_option table created')
        finally:
            await conn.close()

    async def select_lodging_option(self, lodging_option):
        conn = await self.create_conn()
        try:
            loid_obj = await conn.fetchrow(
                'SELECT loid FROM lodging_options WHERE lodging_option_title = $1;', lodging_option)
            loid = str(loid_obj['loid'])
            return loid
        except TypeError as err:
            print(f"No LOID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_lodging_option(self, lodging_option):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO lodging_options (lodging_option_title) VALUES ($1);''', lodging_option)
        finally:
            await conn.close()

    async def insert_to_hotel_lodging_options_table(self, hid, loid):
        # insert_to_hotel_lodging_options_table table.
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_lodging_option (hotel_id, lodging_option_id) VALUES ($1, $2);''', hid, loid)
        finally:
            await conn.close()
