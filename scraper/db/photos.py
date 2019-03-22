import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Photos(MainAsyncConn):

    async def create_table_photo_categories(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS photo_categories")
            await conn.execute(
                "CREATE TABLE photo_categories( \
                    caid uuid DEFAULT uuid_generate_v4 (), \
                    category_name TEXT UNIQUE, \
                    PRIMARY KEY(caid));")
            print('photo_categories table created')
        finally:
            await conn.close()

    async def create_table_photo_sources(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS photo_sources")
            await conn.execute(
                "CREATE TABLE photo_sources( \
                    soid uuid DEFAULT uuid_generate_v4 (), \
                    source_name TEXT UNIQUE, \
                    PRIMARY KEY(soid));")
            print('hotel_photo_categories table created')
        finally:
            await conn.close()

    async def create_table_photo_formats(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS photo_formats")
            await conn.execute(
                "CREATE TABLE photo_formats( \
                    foid uuid DEFAULT uuid_generate_v4 (), \
                    format_name TEXT UNIQUE, \
                    PRIMARY KEY(foid));")
            print('hotel_photo_formats table created')
        finally:
            await conn.close()

    async def create_table_photos(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_photos")
            await conn.execute(
                "CREATE TABLE photos( \
                    phid uuid DEFAULT uuid_generate_v4 (), \
                    category_id uuid, \
                    source_id uuid, \
                    format_id uuid, \
                    hotel_id uuid, \
                    photo_url TEXT, \
                    PRIMARY KEY(phid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE, \
                    FOREIGN KEY (category_id) REFERENCES photo_categories(caid) ON DELETE CASCADE, \
                    FOREIGN KEY (source_id) REFERENCES photo_sources(soid) ON DELETE CASCADE, \
                    FOREIGN KEY (format_id) REFERENCES photo_formats(foid) ON DELETE CASCADE);")
            print('photos table created')
        finally:
            await conn.close()

    async def select_category_id(self, img_category):
        conn = await self.create_conn()
        try:
            caid_obj = await conn.fetchrow(
                'SELECT caid FROM photo_categories WHERE category_name = $1;', img_category)
            caid = str(caid_obj['caid'])
            return caid
        except TypeError as err:
            print(f"No CAID: {err}")
            pass
        finally:
            await conn.close()

    async def select_source_id(self, img_source):
        conn = await self.create_conn()
        try:
            soid_obj = await conn.fetchrow(
                'SELECT soid FROM photo_sources WHERE source_name = $1;', img_source)
            soid = str(soid_obj['soid'])
            return soid
        except TypeError as err:
            print(f"No SOID: {err}")
            pass
        finally:
            await conn.close()

    async def select_format_id(self, img_format):
        conn = await self.create_conn()
        try:
            foid_obj = await conn.fetchrow(
                'SELECT foid FROM photo_formats WHERE format_name = $1;', img_format)
            foid = str(foid_obj['foid'])
            return foid
        except TypeError as err:
            print(f"No FOID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_photo(self, photo_url, caid, hid):
        conn = await self.create_conn()
        try:
            insert = "INSERT INTO photos (photo_url, category_id, hotel_id) VALUES ($1, $2, $3);"
            await conn.execute(insert, photo_url, caid, hid)
        finally:
            await conn.close()

    async def update_source(self, soid, photo_url):
        conn = await self.create_conn()
        try:
            await conn.execute("UPDATE photos SET source_id = $1 WHERE photo_url = $2;", soid, photo_url)
        finally:
            await conn.close()

    async def check_source(self, photo_url):
        conn = await self.create_conn()
        try:
            await conn.execute('''SELECT source_id FROM photos WHERE photo_url = $1;''', photo_url)
        finally:
            await conn.close()

    async def update_format(self, foid, photo_url):
        conn = await self.create_conn()
        try:
            await conn.execute("UPDATE photos SET format_id = $1 WHERE photo_url = $2;", foid, photo_url)
        finally:
            await conn.close()

    async def check_format(self, photo_url):
        conn = await self.create_conn()
        try:
            await conn.execute('''SELECT format_id FROM photos WHERE photo_url = $1;''', photo_url)
        finally:
            await conn.close()
