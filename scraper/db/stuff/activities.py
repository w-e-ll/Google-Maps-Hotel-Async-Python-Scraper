import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Activities(MainAsyncConn):
    async def create_table_activities(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS activities")
            await conn.execute(
                "CREATE TABLE activities( \
                    actid uuid DEFAULT uuid_generate_v4 (), \
                    activity_title TEXT UNIQUE, \
                    PRIMARY KEY(actid));")
            print('activities table created')
        finally:
            await conn.close()

    async def create_table_hotel_activity(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_activity")
            await conn.execute(
                "CREATE TABLE hotel_activity( \
                    hotel_id uuid, \
                    activity_id uuid, \
                    PRIMARY KEY (hotel_id, activity_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (activity_id) REFERENCES activities (actid) ON DELETE CASCADE);")
            print('hotel_activity table created')
        finally:
            await conn.close()

    async def select_activity(self, activity):
        conn = await self.create_conn()
        try:
            actid_obj = await conn.fetchrow(
                'SELECT actid FROM activities WHERE activity_title = $1;', activity)
            actid = str(actid_obj['actid'])
            return actid
        except TypeError as err:
            print(f"No ACTID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_activity(self, activity):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO activities (activity_title) VALUES ($1);''', activity)
        finally:
            await conn.close()

    async def insert_to_hotel_activities_table(self, hid, actid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_activity (hotel_id, activity_id) VALUES ($1, $2);''', hid, actid)
        finally:
            await conn.close()
