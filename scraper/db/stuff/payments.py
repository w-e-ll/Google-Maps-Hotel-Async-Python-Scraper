import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Payments(MainAsyncConn):

    async def create_table_payments(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS payments")
            await conn.execute(
                "CREATE TABLE payments( \
                    pmid uuid DEFAULT uuid_generate_v4 (), \
                    payment_title TEXT UNIQUE, \
                    PRIMARY KEY(pmid));")
            print('payments table created')
        finally:
            await conn.close()

    async def create_table_hotel_payment(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_payment")
            await conn.execute(
                "CREATE TABLE hotel_payment( \
                    hotel_id uuid, \
                    payment_id uuid, \
                    PRIMARY KEY (hotel_id, payment_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (payment_id) REFERENCES payments (pmid) ON DELETE CASCADE);")
            print('hotel_payment table created')
        finally:
            await conn.close()

    async def select_payment(self, payment):
        conn = await self.create_conn()
        try:
            pmid_obj = await conn.fetchrow(
                'SELECT pmid FROM payments WHERE payment_title = $1;', payment)
            pmid = str(pmid_obj['pmid'])
            return pmid
        except TypeError as err:
            print(f"No PMID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_payment(self, payment):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO payments (payment_title) VALUES ($1);''', payment)
        finally:
            await conn.close()

    async def insert_to_hotel_payments_table(self, hid, pmid):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO hotel_payment (hotel_id, payment_id) VALUES ($1, $2);''', hid, pmid)
        finally:
            await conn.close()
