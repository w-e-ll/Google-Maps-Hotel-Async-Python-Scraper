import asyncpg
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class CreateTables:

    def __init__(self):
        pass

    async def create_conn(self):
        conn = await asyncpg.connect(
            user='postgres', password='hftest8H6SEcg', port='5432',
            database='al_hotels', host='192.168.88.252')
        return conn

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

    async def create_table_nearby_things_to_do(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_things_to_do")
            await conn.execute(
                "CREATE TABLE nearby_things_to_do( \
                    nttdid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    thing_name TEXT, \
                    thing_distance_walk VARCHAR(35), \
                    thing_distance_car VARCHAR(35), \
                    thing_distance_bus VARCHAR(35), \
                    thing_img_link TEXT, \
                    PRIMARY KEY(nttdid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_things_to_do table created')
        finally:
            await conn.close()

    async def create_table_nearby_transit_stops(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_transit_stops")
            await conn.execute(
                "CREATE TABLE nearby_transit_stops( \
                    ntsid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    stop_name TEXT, \
                    stop_type VARCHAR(10), \
                    stop_distance VARCHAR(35), \
                    PRIMARY KEY(ntsid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_transit_stops table created')
        finally:
            await conn.close()

    async def create_table_nearby_airports(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS nearby_airports")
            await conn.execute(
                "CREATE TABLE nearby_airports( \
                    naid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    airport_name TEXT, \
                    airport_distance_car VARCHAR(35), \
                    airport_distance_bus VARCHAR(35), \
                    PRIMARY KEY(naid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('nearby_airports table created')
        finally:
            await conn.close()

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

    async def create_table_location_getting_around(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_getting_around")
            await conn.execute(
                "CREATE TABLE location_getting_around( \
                    lgaid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_around_name VARCHAR(150), \
                    location_around_type_text TEXT, \
                    PRIMARY KEY(lgaid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_getting_around table created')
        finally:
            await conn.close()

    async def create_table_location_overview(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_overview")
            await conn.execute(
                "CREATE TABLE location_overview( \
                    lovid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_overview_text TEXT, \
                    PRIMARY KEY(lovid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_overview table created')
        finally:
            await conn.close()

    async def create_table_location_score(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_score")
            await conn.execute(
                "CREATE TABLE location_score( \
                    losid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    score_rate VARCHAR(15), \
                    score_text TEXT, \
                    PRIMARY KEY(losid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_score table created')
        finally:
            await conn.close()

    async def create_table_location_things_to_do(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS location_things_to_do")
            await conn.execute(
                "CREATE TABLE location_things_to_do( \
                    lttdid uuid DEFAULT uuid_generate_v4 (), \
                    hotel_id uuid, \
                    location_thing_name VARCHAR(100), \
                    location_thing_text TEXT, \
                    location_thing_review_rate VARCHAR(20), \
                    location_thing_star_score VARCHAR(10), \
                    location_thing_distance VARCHAR(100), \
                    location_thing_img TEXT, \
                    PRIMARY KEY(lttdid), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel(hid) ON DELETE CASCADE);")
            print('location_score table created')
        finally:
            await conn.close()

    async def create_table_accessibilities(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS accessibilities")
            await conn.execute(
                "CREATE TABLE accessibilities( \
                    acid uuid DEFAULT uuid_generate_v4 (), \
                    accessibility_title TEXT UNIQUE, \
                    PRIMARY KEY(acid));")
            print('accessibilities table created')
        finally:
            await conn.close()

    async def create_table_hotel_accessibility(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_accessibility")
            await conn.execute(
                "CREATE TABLE hotel_accessibility( \
                    hotel_id uuid, \
                    accessibility_id uuid, \
                    PRIMARY KEY (hotel_id, accessibility_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (accessibility_id) REFERENCES accessibilities (acid) ON DELETE CASCADE);")
            print('hotel_accessibility table created')
        finally:
            await conn.close()

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

    async def create_table_crowds(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS crowds")
            await conn.execute(
                "CREATE TABLE crowds( \
                    crid uuid DEFAULT uuid_generate_v4 (), \
                    crowd_title TEXT UNIQUE, \
                    PRIMARY KEY(crid));")
            print('crowds table created')
        finally:
            await conn.close()

    async def create_table_hotel_crowd(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_crowd")
            await conn.execute(
                "CREATE TABLE hotel_crowd( \
                    hotel_id uuid, \
                    crowd_id uuid, \
                    PRIMARY KEY (hotel_id, crowd_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (crowd_id) REFERENCES crowds (crid) ON DELETE CASCADE);")
            print('hotel_crowd table created')
        finally:
            await conn.close()

    async def create_table_fhighlights(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS fhighlights")
            await conn.execute(
                "CREATE TABLE fhighlights( \
                    fhlid uuid DEFAULT uuid_generate_v4 (), \
                    fhighlight_title TEXT UNIQUE, \
                    PRIMARY KEY(fhlid));")
            print('fhighlights table created')
        finally:
            await conn.close()

    async def create_table_hotel_fhighlight(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_fhighlight")
            await conn.execute(
                "CREATE TABLE hotel_fhighlight( \
                    hotel_id uuid, \
                    fhighlight_id uuid, \
                    PRIMARY KEY (hotel_id, fhighlight_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (fhighlight_id) REFERENCES fhighlights (fhlid) ON DELETE CASCADE);")
            print('hotel_fhighlight table created')
        finally:
            await conn.close()

    async def create_table_highlights(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS highlights")
            await conn.execute(
                "CREATE TABLE highlights( \
                    hlid uuid DEFAULT uuid_generate_v4 (), \
                    highlight_title TEXT UNIQUE, \
                    highlight_img_url TEXT, \
                    PRIMARY KEY(hlid));")
            print('highlights table created')
        finally:
            await conn.close()

    async def create_table_hotel_highlight(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_highlight")
            await conn.execute(
                "CREATE TABLE hotel_highlight( \
                    hotel_id uuid, \
                    highlight_id uuid, \
                    PRIMARY KEY (hotel_id, highlight_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (highlight_id) REFERENCES highlights (hlid) ON DELETE CASCADE);")
            print('hotel_highlight table created')
        finally:
            await conn.close()

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

    async def create_table_offerings(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS offerings")
            await conn.execute(
                "CREATE TABLE offerings( \
                    ofid uuid DEFAULT uuid_generate_v4 (), \
                    offering_title TEXT UNIQUE, \
                    PRIMARY KEY(ofid));")
            print('offerings table created')
        finally:
            await conn.close()

    async def create_table_hotel_offering(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_offering")
            await conn.execute(
                "CREATE TABLE hotel_offering( \
                    hotel_id uuid, \
                    offering_id uuid, \
                    PRIMARY KEY (hotel_id, offering_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (offering_id) REFERENCES offerings (ofid) ON DELETE CASCADE);")
            print('hotel_offering table created')
        finally:
            await conn.close()

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

    async def create_table_mapped_urls(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS mapped_urls")
            await conn.execute(
                "CREATE TABLE mapped_urls( \
                    uid uuid DEFAULT uuid_generate_v4 (), \
                    url TEXT, \
                    PRIMARY KEY(uid));")
            print('mapped_urls table created')
        finally:
            await conn.close()

    async def create_table_hotel_mapped_url(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS hotel_mapped_url")
            await conn.execute(
                "CREATE TABLE hotel_mapped_urls( \
                    hotel_id uuid, \
                    url_id uuid, \
                    PRIMARY KEY (hotel_id, url_id), \
                    FOREIGN KEY (hotel_id) REFERENCES hotel (hid) ON DELETE CASCADE, \
                    FOREIGN KEY (url_id) REFERENCES mapped_urls (uid) ON DELETE CASCADE);")
            print('hotel_mapped_url table created')
        finally:
            await conn.close()

    async def create_table_photos(self):
        conn = await self.create_conn()
        try:
            await conn.execute("DROP TABLE IF EXISTS photos")
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

    async def insert_into_photo_categories_sources_formats(self):
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

    async def insert_into_photo_categories(self, category_name):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO photo_categories (category_name) \
                VALUES ($1);''', category_name)
        finally:
            await conn.close()

    async def insert_into_photo_sources(self, source_name):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO photo_sources (source_name) \
                VALUES ($1);''', source_name)
        finally:
            await conn.close()

    async def insert_into_photo_formats(self, format_name):
        conn = await self.create_conn()
        try:
            await conn.execute('''
                INSERT INTO photo_formats (format_name) \
                VALUES ($1);''', format_name)
        finally:
            await conn.close()

    async def create_all_tables(self):
        await self.create_table_hotel()
        await self.create_table_nearby_things_to_do()
        await self.create_table_nearby_transit_stops()
        await self.create_table_nearby_airports()
        await self.create_table_nearby_hotels()
        await self.create_table_location_getting_around()
        await self.create_table_location_overview()
        await self.create_table_location_score()
        await self.create_table_location_things_to_do()
        await self.create_table_accessibilities()
        await self.create_table_hotel_accessibility()
        await self.create_table_activities()
        await self.create_table_hotel_activity()
        await self.create_table_amenities()
        await self.create_table_hotel_amenity()
        await self.create_table_crowds()
        await self.create_table_hotel_crowd()
        await self.create_table_fhighlights()
        await self.create_table_hotel_fhighlight()
        await self.create_table_highlights()
        await self.create_table_hotel_highlight()
        await self.create_table_lodging_options()
        await self.create_table_hotel_lodging_option()
        await self.create_table_offerings()
        await self.create_table_hotel_offering()
        await self.create_table_payments()
        await self.create_table_hotel_payment()
        await self.create_table_plannings()
        await self.create_table_hotel_planning()
        await self.create_table_summary_reviews()
        await self.create_table_hotel_summary_review()
        await self.create_table_reviews_on_other_travel_sites()
        await self.create_table_ratings_by_traveler_type()
        await self.create_table_reviews()
        await self.create_table_mapped_urls()
        await self.create_table_hotel_mapped_url()
        await self.create_table_photo_categories()
        await self.create_table_photo_formats()
        await self.create_table_photo_sources()
        await self.create_table_photos()
        await self.insert_into_photo_categories("Amenities")
        await self.insert_into_photo_categories("Rooms")
        await self.insert_into_photo_categories("Food & Drink")
        await self.insert_into_photo_categories("Exterior")
        await self.insert_into_photo_sources("From visitors")
        await self.insert_into_photo_sources("From property")
        await self.insert_into_photo_formats("Photos")
        await self.insert_into_photo_formats("360° View")

    def create_tables(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_all_tables())


if __name__ == "__main__":
    ct = CreateTables()
    ct.create_tables()
