import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Plannings(MainAsyncConn):

    async def create_table_plannings(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS plannings")
            await conn.execute(
                "CREATE TABLE planning( \
                    plid uuid DEFAULT uuid_generate_v4 (), \
                    planning_title TEXT UNIQUE, \
                    PRIMARY KEY(plid));")
            print('plannings table created')
        finally:
            await conn.close()

    async def create_table_hotel_planning(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_planning")
            await conn.execute(
                "CREATE TABLE hotel_planning( \
                    hotel_id uuid, \
                    planning_id uuid, \
                    PRIMARY KEY (hotel_id, planning_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (planning_id) REFERENCES planning (plid) ON DELETE CASCADE);")
            print('hotel_planning table created')
        finally:
            await conn.close()

    async def select_planning(self, planning):
        conn = await self.create_conn()
        try:
            plid_obj = await conn.fetchrow(
                'SELECT plid FROM planning WHERE planning_title = $1;', planning)
            plid = str(plid_obj['plid'])
            return plid
        except TypeError as err:
            print(f"No PLID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_planning(self, planning):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO planning (planning_title) VALUES ($1);''', planning)
        finally:
            await conn.close()

    async def insert_to_hotel_plannings_table(self, hid, plid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_planning (hotel_id, planning_id) VALUES ($1, $2);''', hid, plid)
        finally:
            await conn.close()
