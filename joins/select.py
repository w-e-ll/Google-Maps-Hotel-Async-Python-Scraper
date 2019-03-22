import asyncpg
import asyncio
import uvloop
import argparse

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
parser = argparse.ArgumentParser()
parser.add_argument('--name', dest='name', type=str,
                    help="input a hotel name (like \"Leipzig Marriott Hotel\")", metavar='')
args = parser.parse_args()


class HotelJoins:
    """
    Get hotel information by name, \
    retrieve data from database. \
    Input a hotel name to get info.
    """

    async def create_conn(self):
        conn = await asyncpg.connect(
            user='postgres', password='hftest8H6SEcg', port='5432',
            database='germany_hotels', host='192.168.88.252')
        return conn

    async def create_conn1(self):
        conn = await asyncpg.connect(
            user='postgres', password='hftest8H6SEcg', port='5432',
            database='germany_hotels_de', host='192.168.88.252')
        return conn

    async def select_airports(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        nearby_airports.airport_name, nearby_airports.airport_distance_car, \
                        nearby_airports.airport_distance_bus, nearby_airports.hotel_id \
                        FROM hotel \
                        JOIN nearby_airports ON nearby_airports.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_things_to_do(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        nearby_things_to_do.hotel_id, nearby_things_to_do.thing_name, \
                        nearby_things_to_do.thing_distance_walk, \
                        nearby_things_to_do.thing_distance_car, \
                        nearby_things_to_do.thing_distance_bus \
                        FROM hotel \
                        JOIN nearby_things_to_do ON nearby_things_to_do.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_train_stops(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        nearby_transit_stops.hotel_id, nearby_transit_stops.stop_name, \
                        nearby_transit_stops.stop_type, \
                        nearby_transit_stops.stop_distance \
                        FROM hotel \
                        JOIN nearby_transit_stops ON nearby_transit_stops.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_highlights(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, highlights.highlight_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_highlight \
                        ON hotel.hid = hotel_highlight.hotel_id \
                        LEFT OUTER JOIN highlights \
                        ON highlights.hlid = hotel_highlight.highlight_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name, highlights.highlight_title;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_fhighlights(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT fhighlights.fhighlight_title, fhighlights.fhlid, hotel.name, hotel.hid \
                        FROM fhighlights \
                        LEFT OUTER JOIN hotel_fhighlight \
                        ON fhighlights.fhlid = hotel_fhighlight.fhighlight_id \
                        LEFT OUTER JOIN hotel \
                        ON hotel_fhighlight.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_amenities(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, amenities.amenity_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_amenity \
                        ON hotel.hid = hotel_amenity.hotel_id \
                        LEFT OUTER JOIN amenities \
                        ON amenities.aid = hotel_amenity.amenity_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_activities(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, activities.activity_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_activity \
                        ON hotel.hid = hotel_activity.hotel_id \
                        LEFT OUTER JOIN activities \
                        ON activities.actid = hotel_activity.activity_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_accessibilities(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, accessibilities.accessibility_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_accessibility \
                        ON hotel.hid = hotel_accessibility.hotel_id \
                        LEFT OUTER JOIN accessibilities \
                        ON accessibilities.acid = hotel_accessibility.accessibility_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_offerings(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, offerings.offering_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_offering \
                        ON hotel.hid = hotel_offering.hotel_id \
                        LEFT OUTER JOIN offerings \
                        ON offerings.ofid = hotel_offering.offering_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_crowds(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, crowds.crowd_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_crowd \
                        ON hotel.hid = hotel_crowd.hotel_id \
                        LEFT OUTER JOIN crowds \
                        ON crowds.crid = hotel_crowd.crowd_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_plannings(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, planning.planning_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_planning \
                        ON hotel.hid = hotel_planning.hotel_id \
                        LEFT OUTER JOIN planning \
                        ON planning.plid = hotel_planning.planning_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_payments(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, payments.payment_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_payment \
                        ON hotel.hid = hotel_payment.hotel_id \
                        LEFT OUTER JOIN payments \
                        ON payments.pmid = hotel_payment.payment_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_lodging_options(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.name, lodging_options.lodging_option_title \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_lodging_option \
                        ON hotel.hid = hotel_lodging_option.hotel_id \
                        LEFT OUTER JOIN lodging_options \
                        ON lodging_options.loid = hotel_lodging_option.lodging_option_id \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_location_overview(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        location_overview.hotel_id, location_overview.location_overview_text \
                        FROM hotel \
                        JOIN location_overview ON location_overview.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_location_score(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, location_score.hotel_id, \
                        location_score.score_rate, \
                        location_score.score_text \
                        FROM hotel \
                        JOIN location_score ON location_score.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_location_things_to_do(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        location_things_to_do.location_thing_name, \
                        location_things_to_do.location_thing_review_rate, \
                        location_things_to_do.location_thing_star_score, \
                        location_things_to_do.location_thing_distance \
                        FROM hotel \
                        JOIN location_things_to_do ON location_things_to_do.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_location_getting_around(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        location_getting_around.hotel_id, \
                        location_getting_around.location_around_name, \
                        location_getting_around.location_around_type_text \
                        FROM hotel \
                        JOIN location_getting_around ON location_getting_around.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_reviews_on_other_travel_sites(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        reviews_on_other_travel_sites.hotel_id, \
                        reviews_on_other_travel_sites.site_name, \
                        reviews_on_other_travel_sites.site_rate, \
                        reviews_on_other_travel_sites.site_img_url \
                        FROM hotel \
                        JOIN reviews_on_other_travel_sites \
                        ON reviews_on_other_travel_sites.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_ratings_by_traveler_type(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        ratings_by_traveler_type.hotel_id, \
                        ratings_by_traveler_type.type_name, \
                        ratings_by_traveler_type.type_rate, \
                        ratings_by_traveler_type.type_img_url \
                        FROM hotel \
                        JOIN ratings_by_traveler_type \
                        ON ratings_by_traveler_type.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_ten_reviews(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        reviews.hotel_id, \
                        reviews.review_author_name, \
                        reviews.review_rating, \
                        reviews.review_timestamp, \
                        reviews.review_text, \
                        reviews.review_img_url \
                        FROM hotel \
                        JOIN reviews ON reviews.hotel_id = hotel.hid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_mapped_urls(self):
        try:
            conn = await self.create_conn1()
            select = '''SELECT hotel.hid, hotel.name, \
                        mapped_urls.url, \
                        mapped_urls.uid \
                        FROM hotel \
                        LEFT OUTER JOIN hotel_mapped_urls \
                        ON hotel_mapped_urls.hotel_id = hotel.hid \
                        LEFT OUTER JOIN mapped_urls \
                        ON hotel_mapped_urls.url_id = mapped_urls.uid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    async def select_photos(self):
        try:
            conn = await self.create_conn()
            select = '''SELECT hotel.hid, hotel.name, \
                        photo_categories.category_name, \
                        photo_sources.source_name, \
                        photo_formats.format_name, \
                        photos.photo_url \
                        FROM hotel \
                        LEFT OUTER JOIN photos \
                        ON photos.hotel_id = hotel.hid \
                        LEFT OUTER JOIN photo_categories \
                        ON photos.category_id = photo_categories.caid \
                        LEFT OUTER JOIN photo_sources \
                        ON photos.source_id = photo_sources.soid \
                        LEFT OUTER JOIN photo_formats \
                        ON photos.format_id = photo_formats.foid \
                        WHERE hotel.name = '{}' \
                        ORDER BY hotel.name;'''.format(args.name)
            result = await conn.fetch(select)
            return result
        finally:
            await conn.close()

    # hotel_joins
    def hotel_joins(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.select_highlights()),
            loop.create_task(self.select_fhighlights()),
            loop.create_task(self.select_amenities()),
            loop.create_task(self.select_activities()),
            loop.create_task(self.select_accessibilities()),
            loop.create_task(self.select_offerings()),
            loop.create_task(self.select_crowds()),
            loop.create_task(self.select_plannings()),
            loop.create_task(self.select_payments()),
            loop.create_task(self.select_lodging_options()),
            loop.create_task(self.select_airports()),
            loop.create_task(self.select_things_to_do()),
            loop.create_task(self.select_train_stops()),
            loop.create_task(self.select_location_overview()),
            loop.create_task(self.select_location_score()),
            loop.create_task(self.select_location_things_to_do()),
            loop.create_task(self.select_location_getting_around()),
            loop.create_task(self.select_reviews_on_other_travel_sites()),
            loop.create_task(self.select_ratings_by_traveler_type()),
            loop.create_task(self.select_ten_reviews()),
            loop.create_task(self.select_mapped_urls()),
            loop.create_task(self.select_photos()),
        ]
        done, pending = loop.run_until_complete(asyncio.wait(
            tasks, return_when=asyncio.ALL_COMPLETED
        ))
        for task in done:
            if task.exception:
                try:
                    loop.run_until_complete(task)
                except Exception as e:
                    print(f'Exception catched: {e}')
        for task in pending:
            task.cancel()
            loop.run_until_complete(task)

        highlights = tasks[0].result()
        fhighlights = tasks[1].result()
        amenities = tasks[2].result()
        activities = tasks[3].result()
        accessibilities = tasks[4].result()
        offerings = tasks[5].result()
        crowds = tasks[6].result()
        plannings = tasks[7].result()
        payments = tasks[8].result()
        lodging_options = tasks[9].result()
        airports = tasks[10].result()
        things_to_do = tasks[11].result()
        train_stops = tasks[12].result()
        location_overview = tasks[13].result()
        location_score = tasks[14].result()
        location_things_to_do = tasks[15].result()
        location_getting_around = tasks[16].result()
        reviews_on_other_travel_sites = tasks[17].result()
        ratings_by_traveler_type = tasks[18].result()
        ten_reviews = tasks[19].result()
        mapped_urls = tasks[20].result()
        photos = tasks[21].result()

        return (highlights, fhighlights, amenities, activities, accessibilities,
                offerings, crowds, plannings, payments, lodging_options, airports,
                things_to_do, train_stops, location_overview, location_score,
                location_things_to_do, location_getting_around, reviews_on_other_travel_sites,
                ratings_by_traveler_type, ten_reviews, mapped_urls, photos)


if __name__ == "__main__":
    hj = HotelJoins()
    hotel = hj.hotel_joins()
    HOTEL_NAME = [value['name'] for value in hotel[0]]
    print(f"HOTEL_NAME: {HOTEL_NAME[0]}")
    print()
    Highlights = [value['highlight_title'] for value in hotel[0]]
    print(f"Highlights: {Highlights}")
    print()
    fhighlights = [value['fhighlight_title'] for value in hotel[1]]
    print(f"fhighlights: {fhighlights}")
    print()
    amenities = [value['amenity_title'] for value in hotel[2]]
    print(f"amenities: {amenities}")
    print()
    activities = [value['activity_title'] for value in hotel[3]]
    print(f"activities: {activities}")
    print()
    accessibilities = [value['accessibility_title'] for value in hotel[4]]
    print(f"accessibilities: {accessibilities}")
    print()
    offerings = [value['offering_title'] for value in hotel[5]]
    print(f"offerings: {offerings}")
    print()
    crowds = [value['crowd_title'] for value in hotel[6]]
    print(f"crowds: {crowds}")
    print()
    plannings = [value['planning_title'] for value in hotel[7]]
    print(f"plannings: {plannings}")
    print()
    payments = [value['payment_title'] for value in hotel[8]]
    print(f"payments: {payments}")
    print()
    lodging_options = [value['lodging_option_title'] for value in hotel[9]]
    print(f"lodging_options: {lodging_options}")
    print()
    airports = hotel[10]
    print(f"airports: {airports}")
    print()
    things_to_do = hotel[11]
    print(f"things_to_do: {things_to_do}")
    print()
    train_stops = hotel[12]
    print(f"train_stops: {train_stops}")
    print()
    location_overview = hotel[13]
    print(f"location_overview: {location_overview}")
    print()
    location_score = hotel[14]
    print(f"location_score: {location_score}")
    print()
    location_things_to_do = hotel[15]
    print(f"location_things_to_do: {location_things_to_do}")
    print()
    location_getting_around = hotel[16]
    print(f"location_getting_around: {location_getting_around}")
    print()
    reviews_on_other_travel_sites = hotel[17]
    print(f"reviews_on_other_travel_sites: {reviews_on_other_travel_sites}")
    print()
    ratings_by_traveler_type = hotel[18]
    print(f"ratings_by_traveler_type: {ratings_by_traveler_type}")
    print()
    ten_reviews = hotel[19]
    print(f"ten_reviews: {ten_reviews}")
    print()
    mapped_urls = hotel[20]
    print(f"mapped_urls: {mapped_urls}")
    print()
    photos = hotel[21]
    print(f"photos: {photos}")
    print()
