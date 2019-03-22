import asyncpg
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class MainAsyncConn():

    def __init__(self):
        pass

    async def create_conn(self):
        conn = await asyncpg.connect(
            user='postgres', password='hftest8H6SEcg', port='5432',
            database='al_hotels', host='192.168.88.252')
        return conn

    async def select_all_hotel_names_from_db(self):
        conn = await self.create_conn()
        try:
            values = await conn.fetch('''SELECT name FROM hotel''')
            names_db = {value['name'] for value in values}
            return names_db
        finally:
            await conn.close()

    async def check_if_hotel_name_is_in_db(self, hname):
        conn = await self.create_conn()
        try:
            hid_obj = await conn.fetchrow(
                'SELECT hid FROM hotel WHERE name = $1', hname)
            hid = str(hid_obj['hid'])
            return hid
        except TypeError as err:
            print(f"No HID: {err}")
            pass
        finally:
            await conn.close()
