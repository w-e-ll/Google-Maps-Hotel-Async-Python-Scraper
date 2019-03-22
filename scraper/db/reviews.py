import asyncpg
import asyncio

from db.main_db import MainAsyncConn


class Reviews(MainAsyncConn):

    async def create_table_summary_reviews(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS summary_reviews")
            await conn.execute(
                "CREATE TABLE summary_reviews( \
                    srid uuid DEFAULT uuid_generate_v4 (), \
                    category VARCHAR(45), \
                    rating  VARCHAR(35), \
                    description TEXT, \
                    PRIMARY KEY(srid));")
            print('summary_reviews table created')
        finally:
            await conn.close()

    async def create_table_hotel_summary_review(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_summary_review")
            await conn.execute(
                "CREATE TABLE hotel_summary_review( \
                    hotel_id uuid, \
                    sreview_id uuid, \
                    PRIMARY KEY (hotel_id, sreview_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (sreview_id) REFERENCES summary_reviews (srid) ON DELETE CASCADE);")
            print('hotel_summary_review table created')
        finally:
            await conn.close()

    async def select_srid(self, stext):
        conn = await self.create_conn()
        try:
            srid_obj = await conn.fetchrow(
                'SELECT srid FROM summary_reviews WHERE description = $1;', stext)
            srid = str(srid_obj['srid'])
            return srid
        except TypeError as err:
            print(f"No SRID: {err}")
            pass
        finally:
            await conn.close()

    async def insert_srid(self, scat, srating, stext):
        conn = await self.create_conn()
        try:
            insert = "INSERT INTO summary_reviews (category, rating, description) VALUES ($1, $2, $3);"
            await conn.execute(insert, scat, srating, stext)
        finally:
            await conn.close()

    async def insert_to_hotel_summary_review_table(self, hid, srid):
        conn = await self.create_conn()
        try:
            insert = "INSERT INTO hotel_summary_review (hotel_id, sreview_id) VALUES ($1, $2);"
            await conn.execute(insert, hid, srid)
        finally:
            await conn.close()

    async def create_table_reviews_on_other_travel_sites(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS reviews_on_other_travel_sites")
            await conn.execute(
                "CREATE TABLE reviews_on_other_travel_sites( \
                    rotsid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    site_name VARCHAR(35), \
                    site_rate VARCHAR(50), \
                    site_img_url TEXT, \
                    PRIMARY KEY(rotsid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('reviews_on_other_travel_sites table created')
        finally:
            await conn.close()

    # async def create_table_hotel_review_on_other_travel_site(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_review_on_other_travel_site")
    #         await conn.execute(
    #             "CREATE TABLE hotel_review_on_other_travel_site( \
    #                 hotel_id uuid, \
    #                 site_id uuid, \
    #                 PRIMARY KEY (hotel_id, site_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (site_id) REFERENCES reviews_on_other_travel_sites (rotsid) ON DELETE CASCADE);")
    #         print('hotel_review_on_other_travel_site table created')
    #     finally:
    #         await conn.close()

    # async def select_rotsid(self, other_site):
    #     conn = await self.create_conn()
    #     try:
    #         rotsid_obj = await conn.fetchrow(
    #             'SELECT rotsid FROM reviews_on_other_travel_sites WHERE site_name = $1;', other_site)
    #         rotsid = str(rotsid_obj['rotsid'])
    #         return rotsid
    #     finally:
    #         await conn.close()

    async def insert_travel_site_review(self, site_name, site_rate, site_img_url, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO reviews_on_other_travel_sites ( \
                        site_name, site_rate, site_img_url, hotel_id) \
                      VALUES ($1, $2, $3, $4);'''
            await conn.execute(insert, site_name, site_rate, site_img_url, hid)
        finally:
            await conn.close()

    # async def insert_to_hotel_review_on_other_travel_site_table(self, hid, rotsid):
    #     conn = await self.create_conn()
    #     try:
    #         insert = "INSERT INTO hotel_review_on_other_travel_site (hotel_id, site_id) VALUES ($1, $2);"
    #         await conn.execute(insert, hid, rotsid)
    #     finally:
    #         await conn.close()

    async def create_table_ratings_by_traveler_type(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS ratings_by_traveler_type")
            await conn.execute(
                "CREATE TABLE ratings_by_traveler_type( \
                    rbttid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    type_name VARCHAR(35), \
                    type_rate VARCHAR(35), \
                    type_img_url TEXT, \
                    PRIMARY KEY(rbttid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('ratings_by_traveler_type table created')
        finally:
            await conn.close()

    # async def create_table_hotel_rating_by_traveler_type(self):
    #     conn = await self.create_conn()
    #     try:
    #         await conn.execute("DROP TABLE IF EXISTS hotel_rating_by_traveler_type")
    #         await conn.execute(
    #             "CREATE TABLE hotel_rating_by_traveler_type( \
    #                 hotel_id uuid, \
    #                 type_id uuid, \
    #                 PRIMARY KEY (hotel_id, type_id), \
    #                 FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
    #                 FOREIGN KEY (type_id) REFERENCES ratings_by_traveler_type (rbttid) ON DELETE CASCADE);")
    #         print('hotel_rating_by_traveler_type table created')
    #     finally:
    #         await conn.close()

    # async def select_rbttid(self, review_type_name):
    #     conn = await self.create_conn()
    #     try:
    #         rbttid_obj = await conn.fetchrow(
    #             'SELECT rbttid FROM ratings_by_traveler_type WHERE type_name = $1;', review_type_name)
    #         rbttid = str(rbttid_obj['rotsid'])
    #         return rbttid
    #     finally:
    #         await conn.close()

    async def insert_rating_by_traveler_type(self, type_name, type_rate, type_img_url, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO ratings_by_traveler_type ( \
                        type_name, type_rate, type_img_url, hotel_id) \
                      VALUES ($1, $2, $3, $4);'''
            await conn.execute(insert, type_name, type_rate, type_img_url, hid)
        finally:
            await conn.close()

    # async def insert_to_hotel_rating_by_traveler_type_table(self, hid, rbttid):
    #     conn = await self.create_conn()
    #     try:
    #         insert = "INSERT INTO hotel_rating_by_traveler_type (hotel_id, type_id) VALUES ($1, $2);"
    #         await conn.execute(insert, hid, rbttid)
    #     finally:
    #         await conn.close()

    async def create_table_reviews(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS reviews")
            await conn.execute(
                "CREATE TABLE reviews( \
                    hrid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    review_author_name VARCHAR(100), \
                    review_rating VARCHAR(35), \
                    review_timestamp TEXT, \
                    review_text TEXT, \
                    review_img_url TEXT, \
                    PRIMARY KEY(hrid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('reviews table created')
        finally:
            await conn.close()

    async def insert_review(self, review_author_name, review_timestamp,
                            review_rating, review_text, review_img_url, hid):
        conn = await self.create_conn()
        try:
            insert = '''INSERT INTO reviews ( \
                            review_author_name, review_timestamp, \
                            review_rating, review_text, review_img_url, hotel_id) \
                        VALUES ($1, $2, $3, $4, $5, $6);'''
            await conn.execute(insert, review_author_name, review_timestamp,
                               review_rating, review_text, review_img_url, hid)
        finally:
            await conn.close()
