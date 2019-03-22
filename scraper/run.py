import os
import sys
import socket
import random
import socks
import asyncpg
import asyncio
import aiohttp
import time
import uvloop
import queue

from aiohttp import ServerDisconnectedError, ServerTimeoutError, ClientConnectorError, ClientError
from concurrent.futures import ThreadPoolExecutor
# from fake_useragent import UserAgent
from lxml import html
from lxml.html import fromstring
from pprint import pprint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from chrome_useragents import chrome

from user_agents import words, words1, names, numbers, numbers1
# from query_list import q_list
from db.main_db import MainAsyncConn
from db.new_hotel import NewHotel
from db.location_highlights import LocationHighlights
from db.location_things_to_do import LocationThingsToDo
from db.location_around import LocationGettingAround
from db.nearby.hotels import Hotels
from db.nearby.things_to_do import Things_to_do
from db.nearby.airports import Airports
from db.nearby.transit_stops import Transit_stops
from db.reviews import Reviews
from db.stuff.amenities import Amenities
from db.stuff.plannings import Plannings
from db.stuff.payments import Payments
from db.stuff.offerings import Offerings
from db.stuff.lodging_options import Lodging_options
from db.stuff.crowds import Crowds
from db.stuff.activities import Activities
from db.stuff.accessibilities import Accessibilities
from db.stuff.highlights import Highlights
from db.stuff.f_highlights import FHighlights
from db.mapped_urls import MappedUrls
from db.photos import Photos

executor = ThreadPoolExecutor(max_workers=4)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
qu = queue.LifoQueue()

# timeout in seconds
timeout = 1000
socket.setdefaulttimeout(timeout)

# ua = UserAgent()
# headers = {}
# headers['User-Agent'] = random.choice(chrome)  # ua.chrome
eheaders = {}
eheaders['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/70.0.3538.110 Chrome/70.0.3538.110 Safari/537.36'

newhotel = NewHotel()
location_highlights = LocationHighlights()
location_thingstodo = LocationThingsToDo()
location_getting_around = LocationGettingAround()
_nearby_hotels = Hotels()
nearby_things_to_do = Things_to_do()
nearby_airports = Airports()
nearby_transit_stops = Transit_stops()
hreviews = Reviews()
amenities = Amenities()
plannings = Plannings()
payments = Payments()
offerings = Offerings()
lodging_options = Lodging_options()
crowds = Crowds()
activities = Activities()
accessibilities = Accessibilities()
_highlights = Highlights()
fhighlights = FHighlights()
mapped_urls = MappedUrls()
photos = Photos()

###################################################


class GoogleSearchHotels(MainAsyncConn):
    """
    Async Spider that scrapes from Google maps hotels data: name, phone, address, website, direction, \
    description, rating, reviews_count, reviews_rating, reviews_link, review, \
    location_highlights, location_things_to_do, location_getting_around, nearby_hotels, \
    earby_things_to_do, nearby_airports, nearby_transit_stops, mapped_urls, photos, ets. \
    Makes a list of queries (need a list of towns, places in country you want to scrape) to be able \
    to make a Google search request. Collects data and stores it to Postgres.
    """
    def __init__(self, *args, **kwargs):
        self.gecko_path = os.path.abspath(os.path.curdir) + '/geckodriver'
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
        self.profile.set_preference("media.peerconnection.enabled", False)
        self.profile.set_preference('javascript.enabled', False)
        self.profile.set_preference("permissions.default.image", 2)
        self.profile.set_preference("permissions.default.stylesheet", 2)
        # self.profile.set_preference("network.http.max-connections", 32)
        # self.profile.set_preference("network.proxy.type", 1)
        # self.profile.set_preference("network.proxy.socks", "127.0.0.1")
        # self.profile.set_preference("network.proxy.socks_port", int(9955))
        self.driver = webdriver.Firefox(firefox_profile=self.profile, executable_path=self.gecko_path)
        self.driver.implicitly_wait(1)
        super(GoogleSearchHotels, self).__init__(*args, **kwargs)

    def get_whoer(self):
        """Get IP"""
        self.driver.get("https://whoer.net")
        time.sleep(5)
        self.driver.quit()

    def get_random_proxy(self, checked):
        """Get random proxy"""
        proxy = random.choice(checked)
        print(f'socks5://{proxy[0]}:{proxy[1]}')
        return f'socks5://{proxy[0]}:{proxy[1]}'

    def button_close(self):
        """Close Iframe if it appears"""
        try:
            iframe = self.driver.find_element_by_xpath("//iframe[@id='hats2-iframe']")
            self.driver.switch_to.frame(iframe)
            self.driver.find_element_by_class_name('hats-close').click()
            self.driver.switch_to.default_content()
        except NoSuchElementException:
            pass

    async def get_ip(self):
        """Close Iframe if it appears"""
        try:
            url = 'http://httpbin.org/ip'
            async with aiohttp.ClientSession(headers=eheaders) as session:
                async with session.get(url) as response:
                    ip = await response.text(encoding='utf-8')
                    return ip
        except Exception as e:
            print('Exception: {}'.format(e))

    def reload(self):
        """Reloads browser"""
        self.driver.refresh()

    def del_from_q_list(self, q):
        """Deletes query from list of queries"""
        with open("query_list.py","r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if q not in line:
                    f.write(line)
            f.truncate()

    def write_to_oldgoogledis_list(self):
        """Writes query to old Google app list"""
        with open('oldgoogledis_list.txt', 'a') as file:
            file.writelines(f'"{q}",' + "\n")

    def get_q_list(self):
        """Gets query list"""
        query_list = open("query_list.py", "r").read()
        q_list = query_list.replace('",', '').replace('"', "").replace('\n\n', '\n').split("\n")
        while '' in q_list:
            q_list.remove('')
        return q_list

    def making_google_query(self, q):
        """Makes request query"""
        str_query = 'hotels in {} Germany'.format(q)
        google_query = str_query.strip().replace("\xc8", "%C8").replace("\xe0", "%E0").replace("\xdc", "%DC").replace(
            "\xf3", "%F3").replace("\xdf", "%DF").replace("\xd6", "%D6").replace("\xe8", "%E8").replace(
            "\u2122", "%u2122").replace("\xf4", "%F4").replace("\xc4", "%C4").replace("\xe2", "%E2").replace(
            "\xe4", "%E4").replace("\xfc", "%FC").replace("\xe9", "%E9").replace("\xf6", "%F6").replace(" ", "%20").replace(
            "&", "%26").replace("'", "%27").replace("*", "%2A").replace("|", "%7C").replace("\'n", "%5C%27n").replace(
            "\'", "%5C%27").replace("/", "%2F").replace(" ", "%2B")
        print("google_query: {}".format(google_query))
        return google_query

    async def async_google_query(self, loop):
        try:
            future = loop.run_in_executor(executor, self.making_google_query)
            result = await asyncio.wait_for(future, timeout=2, loop=loop)
            return result
        except asyncio.TimeoutError as e:
            print(f"asyncio.TimeoutError {str(e)}")
            import datetime
            print(datetime.datetime.now())
            pass

    # first set of tasks
    def first_set_of_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_ip()),
            loop.create_task(self.async_google_query(loop)),
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

        google_query_list = tasks[1].result()
        return google_query_list

    ##################################

    def google_request(self, google_query):
        """Making Google request"""
        self.driver.get("https://www.google.com/search?hl=en&q={}".format(google_query))

    def check_block(self):
        """Checks existance of hotel block"""
        try:
            check_block = self.driver.find_element_by_xpath('//div/div[@class="MWjNvc"]').text
            return check_block
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    def check_block1(self):
        """Checks existance of hotel block1"""
        try:
            check_block = self.driver.find_element_by_class_name("xHu8gf").text
            return check_block1
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    def check_button(self):
        """Check button"""
        try:
            check_button = self.driver.find_element_by_class_name("zkIadb").text
            return check_button
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def click_in_google(self):
        """Clicks on hotel block"""
        button = self.driver.find_element_by_class_name("MWjNvc").get_attribute('data-url')
        url = 'https://google.com' + button
        print(f"DATA URL MWjNvc: {url[:40]}")
        self.driver.get(url)

    def click_in_google1(self):
        """Clicks on hotel block1"""
        button = self.driver.find_element_by_class_name("xHu8gf").get_attribute('data-url')
        url = 'https://google.com' + button
        print(f"DATA URL xHu8gf: {url[:40]}")
        self.driver.get(url)

    async def click_finish_button(self):
        """Clicks ofinish button"""
        try:
            button_finish = self.driver.find_element_by_tag_name("g-raised-button")
            await asyncio.sleep(1)
            button_finish.click()
        except NoSuchElementException as err:
            print("{}".format("No such button + {}".format(err)))
            pass

    ##################################

    def now_get_current_url(self):
        """Gets current url"""
        current_url = self.driver.current_url
        return current_url

    def click_to_get_back(self, get_back_url):
        """Clicks back"""
        self.driver.get(get_back_url)

    async def collect_hotel_links(self):
        """Collects hotel links"""
        try:
            hotel_obj_links = self.driver.find_elements_by_xpath(
                '//div[@class="uaTTDe UcV03e hCTmhf aAHsSd"]/a')
            print("Collecting hotel_links: {}".format(len(hotel_obj_links)))
            hotel_links = [obj.get_attribute("href") for obj in hotel_obj_links]
            return hotel_links
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def collect_hotel_names(self):
        """Collects hotel names"""
        try:
            hotels_obj_names = self.driver.find_elements_by_class_name('Nj1rKd')
            hnames = [n.text for n in hotels_obj_names]
            print("Collecting hotel objs names: {}".format(len(hnames)))
            return hnames
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    # name_task
    def name_task(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.collect_hotel_names()),
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

        h_names = tasks[0].result()
        return h_names

    # third set of tasks
    def third_set_of_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.collect_hotel_links()),
            loop.create_task(self.collect_hotel_names()),
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

        h_links = tasks[0].result()
        h_names = tasks[1].result()
        return list(zip(h_links, h_names))

    ##################################

    # fourth set of tasks
    def fourth_task(self):
        loop = asyncio.get_event_loop()
        all_db_names = loop.run_until_complete(self.select_all_hotel_names_from_db())
        return all_db_names

    ##################################

    async def hotel_link_click(self, obj):
        """Get to hotel obj, click it"""
        try:
            self.driver.get(obj)
            await asyncio.sleep(3)
        except NoSuchElementException as err:
            print("{}".format(err))
            self.reload()

    def click_on_obj(self, obj):
        """Get to hotel obj, click it"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.hotel_link_click(obj))

    ###################################

    async def get_nearby_hotels(self):
        """Get nearby hotels"""
        try:
            nearby_objs = self.driver.find_elements_by_class_name('qZg7mb')
            nearby_hotel_objs = [nearby_obj.text.split("\n") for nearby_obj in nearby_objs]
            for obj in nearby_hotel_objs:
                if '\ue838' in obj:
                    while '\ue838':
                        try:
                            obj.remove('\ue838')
                        except ValueError:
                            break
            for nearby in nearby_hotel_objs:
                if 'km' in nearby[-1]:
                    pass
                else:
                    del nearby[-1]
            for nearby in nearby_hotel_objs:
                try:
                    if nearby[-2].startswith("("):
                        nearby.insert(3, '-')
                except IndexError as err:
                    print(f'No nearby[-2]: {err}')
            return nearby_hotel_objs
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    def get_hotel_nearby_hotels(self):
        loop = asyncio.get_event_loop()
        nearby_hotel_objs = loop.run_until_complete(self.get_nearby_hotels())
        return nearby_hotel_objs

    async def get_nearby_hotels_imgs(self):
        """Get nearby hotel images"""
        try:
            nearby_img_objs = self.driver.find_elements_by_class_name('lj7Jje')
            nearby_hotel_imgs = [obj.get_attribute("src") for obj in nearby_img_objs]
            return nearby_hotel_imgs
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    def get_hotel_nearby_hotel_imgs(self):
        loop = asyncio.get_event_loop()
        nearby_hotel_imgs = loop.run_until_complete(self.get_nearby_hotels_imgs())
        return nearby_hotel_imgs

    ###################################

    async def click_to_open_location(self):
        """Click to open location"""
        try:
            self.driver.find_element_by_id("location").click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def open_location(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_location())

    ##################################

    async def get_location_overview_text(self):
        """Get location overview text"""
        try:
            location_overview_obj = self.driver.find_element_by_class_name('kpR9vc').text
            location_overview = location_overview_obj.split("\n")
            location_overview_text = location_overview[-1]
            return location_overview_text
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_location_score(self):
        """Get location score"""
        location_score_obj = self.driver.find_elements_by_class_name('lUFEkc')
        location_score = [obj.text for obj in location_score_obj]
        if location_score[0] == '':
            score_rates = None
            score_texts = None
        else:
            score = location_score[1].split("\n")
            if '\ue3b0' in score:
                score.remove('\ue3b0')
            if '\ue535' in score:
                score.remove('\ue535')
            if '\ue195' in score:
                score.remove('\ue195')
            if 'Hotel Location Score' in score:
                score.remove('Hotel Location Score')
            for i in score:
                if i.startswith("Scores are calculated"):
                    score.remove(i)
            score_rates = score[::2]
            score_texts = score[1::2]
            if len(score_rates) >= 15:
                score_rates = None
                score_rates = None
        return list(zip(score_rates, score_texts))

    def get_location_highlights(self):
        """Get location highlights"""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_location_overview_text()),
            loop.create_task(self.get_location_score()),
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

        location_overview_text = tasks[0].result()
        location_score = tasks[1].result()
        return location_overview_text, location_score

    ########################################

    def get_to_location_things_to_do(self):
        """Get location things to do"""
        try:
            self.driver.find_element_by_id('topsights').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    async def get_things_to_do(self):
        """Get things to do"""
        location_things_objs = self.driver.find_elements_by_class_name('uaTTDe')
        location_things_objs_all = [obj.text for obj in location_things_objs]
        while '' in location_things_objs_all:
            location_things_objs_all.remove('')
        location_things = []
        for obj in location_things_objs_all:
            new = obj.split('\n')
            location_things.append(new)
        location_things_to_do = location_things
        for obj in location_things_to_do:
            while '\ue838' in obj:
                obj.remove('\ue838')
        for obj in location_things_to_do:
            while 'Distance' in obj:
                obj.remove('Distance')
        return location_things_to_do

    async def get_location_things_imgs(self):
        """Get location things to do images"""
        location_things_imgs_objs = self.driver.find_elements_by_class_name('Mp5Une')
        location_things_imgs = [obj.get_attribute("src") for obj in location_things_imgs_objs]
        return location_things_imgs

    def get_location_things_to_do(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_things_to_do()),
            loop.create_task(self.get_location_things_imgs())
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

        location_things_to_do = tasks[0].result()
        location_things_imgs = tasks[1].result()
        return location_things_to_do, location_things_imgs

    def get_to_location_getting_around(self):
        """Get to location getting around"""
        try:
            self.driver.find_element_by_id('transit').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    async def get_getting_around(self):
        """Get location getting around"""
        objs_to_close = self.driver.find_elements_by_class_name('sMVRZe')
        objs_to_close[1].click()
        getting_around_objs = self.driver.find_elements_by_class_name('ebwxJ')
        getting_around_objs_names = self.driver.find_elements_by_class_name('vC46ub')
        getting_around_names = [i.text for i in getting_around_objs_names]
        g_arounds = list(zip(getting_around_names, getting_around_objs))
        getting_arounds = []
        for around_name, around_obj in g_arounds:
            around_obj.click()
            if around_name == 'Transit stops':
                arounds_objs = self.driver.find_elements_by_class_name('KPeyce')
                arounds_row = [i.text for i in arounds_objs]
                while '' in arounds_row:
                    arounds_row.remove('')
                transit_arounds = []
                for around in arounds_row:
                    if around.startswith('\ue530'):
                        new_around = around.replace("\ue530\n", "Bus: ").replace("\n\ue536", " walking")
                        transit_arounds.append(new_around)
                    if around.startswith('\ue533'):
                        new_around = around.replace("\ue533\n", "Train: ").replace("\n\ue536", " walking")
                        transit_arounds.append(new_around)
                    if around.startswith('\ue571'):
                        new_around = around.replace("\ue571\n", "Tram: ").replace("\n\ue536", " walking")
                        transit_arounds.append(new_around)
                location_around_transit_stops = around_name, transit_arounds
                getting_arounds.append(location_around_transit_stops)
            else:
                arounds_objs = self.driver.find_elements_by_class_name('KPeyce')
                arounds_row = [i.text for i in arounds_objs]
                while '' in arounds_row:
                    arounds_row.remove('')
                airport_arounds = []
                for around in arounds_row:
                    if around.startswith('\ue559'):
                        new_around = around.replace("\ue559\n", "By ").replace("\n\ue192", ":")
                        airport_arounds.append(new_around)
                    if around.startswith('\ue530'):
                        new_around = around.replace("\ue530\n", "By ").replace("\n\ue192", ":")
                        airport_arounds.append(new_around)
                location_around_airports = around_name, airport_arounds
                getting_arounds.append(location_around_airports)
        return getting_arounds

    def get_location_getting_around(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_getting_around())
        return result

    ########################################

    async def get_nearby(self):
        """Get nearby hotels"""
        try:
            nears_objs = self.driver.find_elements_by_class_name('uaTTDe')
            near_objs_all = [near_obj.text.split("\n") for near_obj in nears_objs]
            near_objs = near_objs_all[:3]
            for obj in near_objs:
                obj.remove('Nearby')
            if '\ue535' in near_objs[1]:
                near_objs[1].remove('\ue535')
            if '\ue53d' in near_objs[2]:
                near_objs[2].remove('\ue53d')
            for i in near_objs:
                if i[0] == 'Transit stops':
                    if not i[3].startswith("\ue536"):
                        i.insert(3, '\ue536 - min')
            for i in near_objs:
                if i[0] == 'Transit stops':
                    if not i[6].startswith("\ue536"):
                        i.insert(6, '\ue536 - min')
            for i in near_objs:
                if i[0] == 'Transit stops':
                    if not i[9].startswith("\ue536"):
                        i.insert(9, '\ue536 - min')
            names = [n[0] for n in near_objs]
            img_objs = self.driver.find_elements_by_xpath('//div[@class="hdNX9c"]/a/img')
            objs = [obj.get_attribute("src") for obj in img_objs]
            nearby_imgs = objs
            nearby_objs = []
            for obj in near_objs:
                i = 1
                obj_list = []
                while i < len(obj):
                    x = obj[i:i + 3]
                    i += 3
                    obj_list.append(x)
                nearby_objs.append(obj_list)
            return nearby_objs, nearby_imgs
        except IndexError as err:
            print(f"Can't find nearby objs: {err}")
            # connection_attempts += 1
            pass
        except NoSuchElementException as err:
            print("{}".format(err))
            return None, None
        except ValueError as err:
            print("{}".format(err))
            return None, None

    def get_hotel_nearby(self):
        loop = asyncio.get_event_loop()
        nearby_objs, nearby_imgs = loop.run_until_complete(self.get_nearby())
        return nearby_objs, nearby_imgs

    ###################################

    async def get_hotel_adds(self):
        """Get hotel adds"""
        try:
            adds = self.driver.find_element_by_class_name('Dhct3d').text
            if adds:
                return True
        except NoSuchElementException as err:
            print("{}".format(err))
            return False

    async def get_hotel_name(self):
        """Get hotel name"""
        try:
            name = self.driver.find_element_by_class_name('SIgVo').text
            print("NAME: {}".format(name))
            return name
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_website(self):
        """Get hotel website"""
        try:
            objs = self.driver.find_elements_by_xpath('//span[@class="YVWGD"]/a')
            objs_hrefs = [obj.get_attribute("href") for obj in objs]
            for obj in objs_hrefs:
                if 'https://maps.google.com' in obj:
                    pass
                else:
                    website = obj
                    return website
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_direction(self):
        """Get hotel direction"""
        try:
            objs = self.driver.find_elements_by_xpath('//span[@class="YVWGD"]/a')
            objs_hrefs = [obj.get_attribute("href") for obj in objs]
            for obj in objs_hrefs:
                if 'https://maps.google.com' in obj:
                    direction = obj
                    return direction
                else:
                    pass
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_rating(self):
        """Get hotel rating"""
        try:
            rating = self.driver.find_element_by_xpath(
                '//div[@class="zjPIAb"]/span[@class="NdB0db"]').text
            return rating
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_reviews_count(self):
        """Get hotel reviews count"""
        try:
            text = self.driver.find_element_by_class_name('dnqv9e').text
            count = self.driver.find_element_by_class_name('TMjBvf').text
            reviews_count = str(text + ': ' + count)
            return reviews_count
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_reviews_rating(self):
        try:
            reviews_rating = self.driver.find_element_by_class_name('EGb1Ef').text
            return reviews_rating
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_address_and_phone(self):
        """Get hotel address and phone"""
        try:
            address_obj = self.driver.find_element_by_class_name('jjuKhc').text
            if '•' in address_obj:
                obj = address_obj.split("•")
                address = obj[0]
                phone = obj[-1]
                return address, phone
            else:
                address = address_obj
                phone = None
                return address, phone
        except NoSuchElementException as err:
            print("{}".format(err))
            return None, None

    async def get_hotel_phone(self):
        """Get hotel phone"""
        try:
            phone_objs = self.driver.find_elements_by_class_name('NdB0db')
            phone = phone_objs[-1].text
            return phone
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_short_review(self):
        """Get hotel short_review"""
        try:
            short_review = self.driver.find_element_by_class_name('a8zsCc').text
            return short_review
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    # fifth set of tasks
    def fifth_set_of_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_hotel_adds()),
            loop.create_task(self.get_hotel_name()),
            loop.create_task(self.get_hotel_website()),
            loop.create_task(self.get_hotel_direction()),
            loop.create_task(self.get_hotel_rating()),
            loop.create_task(self.get_hotel_reviews_count()),
            loop.create_task(self.get_hotel_reviews_rating()),
            loop.create_task(self.get_hotel_address_and_phone()),
            loop.create_task(self.get_hotel_short_review()),
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

        adds = tasks[0].result()
        name = tasks[1].result()
        website = tasks[2].result()
        direction = tasks[3].result()
        rating = tasks[4].result()
        reviews_count = tasks[5].result()
        reviews_rating = tasks[6].result()
        address, phone = tasks[7].result()
        short_review = tasks[8].result()

        return (adds, name, website, direction, rating,
                reviews_count, reviews_rating, address,
                phone, short_review)

    ##################################

    async def click_to_open_description(self):
        """Click to open description"""
        try:
            self.driver.find_element_by_id('details').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def open_description(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_description())

    ##################################

    async def get_hotel_description(self):
        """Get hotel description"""
        try:
            description_objs = self.driver.find_elements_by_class_name('ihh2Je')
            descriptions = [obj.text for obj in description_objs]
            description = ' '.join(descriptions)
            return description
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_highlights(self):
        """Get hotel highlights"""
        try:
            highlights_img_objs = self.driver.find_elements_by_class_name('AMgzG')
            highlights_imgs = [img_obj.get_attribute("src") for img_obj in highlights_img_objs]
            highlights_text_objs = self.driver.find_elements_by_class_name('wHFz0b')
            highlights_texts = [text_obj.text for text_obj in highlights_text_objs]
            return highlights_imgs, highlights_texts
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_facilities(self):
        """Get hotel facilities"""
        try:
            names = ["Amenities", "Accessibility", "Activities", "Crowd",
                     "Lodging options", "Offerings", "Payments", "Planning", "Highlights"]
            objs = self.driver.find_elements_by_xpath('//dl[@class="iUkQ9 AQYYoe"]')
            texts = [obj.text.split("\n")[::2] for obj in objs]
            names = [text.pop(0) for text in texts]
            zipped = dict(zip(names, texts))
            return zipped
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    # description tasks
    def description_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_hotel_description()),
            loop.create_task(self.get_hotel_highlights()),
            loop.create_task(self.get_hotel_facilities()),
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

        description = tasks[0].result()
        highlights_imgs, highlights_texts = tasks[1].result()
        facilities = tasks[2].result()

        return (description, highlights_imgs, highlights_texts, facilities)

    ##################################

    async def click_to_open_reviews(self):
        """Click to open reviews"""
        try:
            self.driver.find_element_by_id('reviews').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def open_reviews(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_reviews())

    ##################################

    async def get_hotel_reviews_on_other_travel_sites(self):
        """Get hotel reviews on other travel sites"""
        try:
            reviews_objs = self.driver.find_elements_by_class_name("VeZivf")
            reviews_row = [obj.text for obj in reviews_objs]
            reviews = reviews_row[8:]
            reviews_on_other_sites = [review.split("\n") for review in reviews]
            reviews_img_objs = self.driver.find_elements_by_class_name("JXQCR")
            reviews_img_row = [obj.get_attribute("src") for obj in reviews_img_objs]
            reviews_imgs = reviews_img_row[8:]
            return reviews_on_other_sites, reviews_imgs
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    async def get_hotel_ratings_by_traveler_type(self):
        """Get hotel ratings by traveler type"""
        try:
            ratings_objs = self.driver.find_element_by_class_name('dLjkKb').text
            ratings = list(ratings_objs.split('\n'))
            type_names = ratings[::2]
            type_rates = ratings[1::2]
            ratings_img_objs = self.driver.find_elements_by_class_name('IRRQCd')
            ratings_imgs = [obj.get_attribute("src") for obj in ratings_img_objs]
            return type_names, type_rates, ratings_imgs
        except NoSuchElementException as err:
            print("{}".format(err))
            return None, None, None

    async def get_hotel_first_ten_reviews(self):
        """Get hotel first ten reviews"""
        try:
            ten_reviews_objs = self.driver.find_elements_by_class_name('cdLULb')
            reviews_row = [obj.text for obj in ten_reviews_objs]
            reviews_list = [r.split('\n') for r in reviews_row]
            error_k = ['E', 'B', 'A', 'W', 'H', 'O', 'T', 'C', 'M', 'N', 'K', 'L', 'Y', 'J', 'S', 'D', 'V']
            for review in reviews_list:
                for e in error_k:
                    if e in review:
                        review.remove(e)
                    if 'ago on Google' in review[0]:
                        review.insert(0, 'none')

            ten_reviews_img_objs = self.driver.find_elements_by_class_name('ZCWdM')
            ten_reviews_imgs = [obj.get_attribute("src") for obj in ten_reviews_img_objs]
            return reviews_list, ten_reviews_imgs
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    # description tasks
    def reviews_page_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_hotel_reviews_on_other_travel_sites()),
            loop.create_task(self.get_hotel_ratings_by_traveler_type()),
            loop.create_task(self.get_hotel_first_ten_reviews()),
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

        reviews_on_other_sites, reviews_imgs = tasks[0].result()
        type_names, type_rates, ratings_imgs = tasks[1].result()
        reviews_list, ten_reviews_imgs = tasks[2].result()

        return (reviews_on_other_sites, reviews_imgs, type_names,
                type_rates, ratings_imgs, reviews_list, ten_reviews_imgs)

    ##################################

    async def click_to_open_photos(self):
        """Click to open photos"""
        try:
            self.driver.find_element_by_id('photos').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def open_photos(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_photos())

    ##################################

    async def click_to_open_categories(self):
        """Click to open categories"""
        button_objs = self.driver.find_elements_by_xpath('//div[@class="jgvuAb rRDaU yJkB0b Y4qIIc"]')
        time.sleep(1)
        button_objs[0].click()

    async def get_category_objs(self):
        """Get category objs"""
        try:
            category_objs = self.driver.find_elements_by_xpath('//div[@class="OA0qNb ncFHed"]/div')
            if category_objs:
                category_objs[0].click()
            return category_objs
        except NoSuchElementException as err:
            print("{}".format("No category_objs + {}".format(err)))
            pass

    async def get_blank_categories(self):
        """Get blank categories"""
        try:
            objs_no = self.driver.find_elements_by_xpath(
                '//div[@class="OA0qNb ncFHed"]/div[@class="MocG8c bvA5be LMgvRb RDPZE"]')
            obj_no = [i.text for i in objs_no]
            return obj_no
        except NoSuchElementException as err:
            print("{}".format("No such button + {}".format(err)))
            return None

    async def get_to_bottom(self):
        """Get to bottom"""
        SCROLL_PAUSE_TIME = 1.5
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    async def get_images(self):
        """Get images"""
        image_objs = self.driver.find_elements_by_class_name('ssXEcf')
        images = [i.get_attribute("src") for i in image_objs]
        return images

    async def get_start_obj(self):
        """Get start_obj"""
        obj_start = self.driver.find_element_by_xpath(
            '//div[@class="OA0qNb ncFHed"]/div[@class="MocG8c bvA5be LMgvRb KKjvXb"]')
        obj_start.click()

    async def get_yes_objs(self):
        """Get yes_objs"""
        obj_yes = self.driver.find_elements_by_xpath(
            '//div[@class="OA0qNb ncFHed"]/div[@class="MocG8c bvA5be LMgvRb"]')
        str_yes = {obj.text for obj in obj_yes}
        cat = dict(zip(str_yes, obj_yes))
        return cat

    async def check_categories(self):
        """check_categories"""
        categories = {'Alle Kategorien', 'Ausstattung', 'Zimmer', 'Essen & Trinken', 'Außenbereich'}
        print(f"Default categories: {categories}")
        await self.click_to_open_categories()
        obj_no = await self.get_blank_categories()
        print(f"OBJ_NO: {obj_no}")
        for i in categories.copy():
            if i in obj_no:
                categories.remove(i)
        print(f"Categories to scrape: {categories}")
        print(f"I'm here... SLEEP")
        time.sleep(1)
        await self.get_category_objs()
        return categories

    async def get_all_category(self):
        """Get all category"""
        await self.click_to_open_categories()
        await self.get_start_obj()
        await self.get_to_bottom()
        all_category_images = await self.get_images()
        print(f"LEN All_category_images: {len(all_category_images)}")
        return all_category_images

    # img_category_tasks
    def img_category_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.check_categories()),
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

        categories = tasks[0].result()
        return (categories)

    # img_category_first_task_set
    def img_category_first_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.click_to_open_categories()),
            loop.create_task(self.get_yes_objs()),
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

        cat = tasks[1].result()
        return cat

    async def get_img_category(self):
        """Get image_category"""
        image_category_objs = self.driver.find_elements_by_xpath(
            '//div[@class="ry3kXd Ulgu9"]/div[@class="MocG8c bvA5be LMgvRb KKjvXb"]/content/span')
        image_categories = [image_category.text for image_category in image_category_objs]
        img_category = image_categories[5:6]
        return img_category

    # img_category_second_task_set
    def img_category_second_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_to_bottom()),
            loop.create_task(self.get_img_category()),
            loop.create_task(self.get_images()),
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

        img_category = tasks[1].result()
        images = tasks[2].result()
        return img_category, images

    async def get_img_source(self):
        """Get image source"""
        image_source_objs = self.driver.find_elements_by_xpath(
            '//div[@class="ry3kXd Ulgu9"]/div[@class="MocG8c bvA5be LMgvRb KKjvXb"]/content/span')
        image_sources = [image_source.text for image_source in image_source_objs]
        img_source = image_sources[-3]
        return img_source

    # img_source_second_task_set
    def img_source_second_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_to_bottom()),
            loop.create_task(self.get_img_source()),
            loop.create_task(self.get_images()),
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

        img_source = tasks[1].result()
        images = tasks[2].result()
        return img_source, images

    async def get_img_format(self):
        """Get image format"""
        image_format_objs = self.driver.find_elements_by_xpath(
            '//div[@class="ry3kXd Ulgu9"]/div[@class="MocG8c bvA5be LMgvRb KKjvXb"]/content/span')
        image_formats = [image_format.text for image_format in image_format_objs]
        img_format = image_formats[-1]
        return img_format

    # img_source_second_task_set
    def img_format_second_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_to_bottom()),
            loop.create_task(self.get_img_format()),
            loop.create_task(self.get_images()),
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

        img_format = tasks[1].result()
        images = tasks[2].result()
        return img_format, images

    # img_category_pre_last_task
    def img_category_pre_last_task(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_categories())

    # img_category_last_task
    def img_category_last_task(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_category_objs())

    ##################################

    async def click_to_open_sources(self):
        """Click to open sources"""
        button_objs = self.driver.find_elements_by_xpath(
            '//div[@class="jgvuAb rRDaU yJkB0b Y4qIIc"]')
        time.sleep(1)
        button_objs[1].click()

    async def check_sources(self):
        """Check sources"""
        sources = {'Alle Quellen', 'Von Gästen', 'Vom Hotel'}
        print(f"Default sources: {sources}")
        await self.click_to_open_sources()
        obj_no = await self.get_blank_categories()
        for i in sources.copy():
            if i in obj_no:
                sources.remove(i)
        print(f"Sources to scrape: {sources}")
        await self.get_category_objs()
        return sources

    async def get_all_sources(self):
        """Get all sources"""
        await self.click_to_open_sources()
        await self.get_start_obj()
        await self.get_to_bottom()
        all_sources_images = await self.get_images()
        print(f"LEN All_sources_images: {len(all_sources_images)}")
        return all_sources_images

    # img_sources_tasks
    def img_sources_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.check_sources()),
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

        sources = tasks[0].result()
        # all_sources_images = tasks[1].result()
        return (sources)

    # img_sources_first_task_set
    def img_sources_first_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.click_to_open_sources()),
            loop.create_task(self.get_yes_objs()),
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

        sour = tasks[1].result()
        return sour

    # img_sources_pre_last_task
    def img_sources_pre_last_task(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_sources())

    ##################################

    async def click_to_open_formats(self):
        """Click to open formats"""
        button_objs = self.driver.find_elements_by_xpath(
            '//div[@class="jgvuAb rRDaU yJkB0b Y4qIIc"]')
        time.sleep(1)
        button_objs[2].click()

    async def check_formats(self):
        """Check formats"""
        formats = {'Alle Formate', '360°-Ansicht', 'Fotos'}
        print(f"Default formats: {formats}")
        await self.click_to_open_formats()
        obj_no = await self.get_blank_categories()
        for i in formats.copy():
            if i in obj_no:
                formats.remove(i)
        print(f"Formats to scrape: {formats}")
        await self.get_category_objs()
        return formats

    async def get_all_formats(self):
        """Get all formats"""
        await self.click_to_open_formats()
        await self.get_start_obj()
        await self.get_to_bottom()
        all_formats_images = await self.get_images()
        print(f"LEN All_formats_images: {len(all_formats_images)}")
        return all_formats_images

    # img_formats_tasks
    def img_formats_tasks(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.check_formats()),
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

        formats = tasks[0].result()
        # all_formats_images = tasks[1].result()
        return (formats)

    # img_formats_first_task_set
    def img_formats_first_task_set(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.click_to_open_formats()),
            loop.create_task(self.get_yes_objs()),
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

        iform = tasks[1].result()
        return iform

    # img_formats_pre_last_task
    def img_formats_pre_last_task(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_formats())

    ##################################

    async def click_to_open_prices(self):
        """Click to open prices"""
        try:
            self.driver.find_element_by_id('prices').click()
        except NoSuchElementException as err:
            print("{}".format(err))
            pass

    def open_prices(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.click_to_open_prices())

    ##################################

    async def get_hotel_links_to_map(self):
        """Get hotel links to map"""
        try:
            a_links_objs = self.driver.find_elements_by_class_name('KGcjV')
            a_links = [obj.get_attribute("href") for obj in a_links_objs]
            return a_links
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    def async_get_hotel_links_to_map(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_hotel_links_to_map())
        return result

    async def fetch(self, session, link):
        async with session.get(link) as response:
            return response.url

    async def main(self, link):
        header = {}
        agent = ['{}:{}:v{}.{} (by /u/{})'.format(
            random.choice(words), random.choice(words1),
            random.choice(numbers), random.choice(numbers1), random.choice(names))]
        header['User-Agent'] = random.choice([agent])
        header = {'User-Agent': random.choice(header['User-Agent'])}
        print('Agent-Smith: {}'.format(header))
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(headers=header, timeout=timeout) as session:
                url = await self.fetch(session, link)
                return url
        except asyncio.TimeoutError as e:
            print(f"asyncio.TimeoutError {str(e)}")
            import datetime
            print(datetime.datetime.now())
            pass

    def get_redirects(self, link):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.main(link))
        return result

    ##################################

    def get_hotel_reviews_query(self, hname, address):
        r_query = 'hotel+"' + hname + '"+' + address
        reviews_query = r_query.strip().replace("\xc8", "%C8").replace(
            "\xe0", "%E0").replace("\xdc", "%DC").replace("\xf3", "%F3").replace("\xdf", "%DF").replace(
            "\xd6", "%D6").replace("\xe8", "%E8").replace("\u2122", "%u2122").replace("\xf4", "%F4").replace(
            "\xc4", "%C4").replace("\xe2", "%E2").replace("\xe4", "%E4").replace("\xfc", "%FC").replace(
            "\xe9", "%E9").replace("\xf6", "%F6").replace(" ", "%20").replace("&", "%26").replace(
            "'", "%27").replace("*", "%2A").replace("|", "%7C").replace("\'n", "%5C%27n").replace(
            "\'", "%5C%27").replace("/", "%2F").replace(" ", "%2B")
        return reviews_query

    async def make_request_to_get_summary_reviews(self, hname, address):
        reviews_query = self.get_hotel_reviews_query(hname, address)
        print("Reviews Query: {}".format(reviews_query))
        url = 'https://www.google.com/search?hl=en&q={}'.format(reviews_query)
        print('Fetching: {}'.format(url))
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(headers=eheaders, timeout=timeout) as session:
                async with session.get(url) as response:
                    html_obj = await response.text(encoding='utf-8')
                    html_tree = html.fromstring(html_obj)
                    return html_tree
        except asyncio.TimeoutError as e:
            print(f"asyncio.TimeoutError {str(e)}")
            import datetime
            print(datetime.datetime.now())
            pass
        except Exception as e:
            print('Exception: {}'.format(e))
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    # six set of tasks
    def six_task(self, hname, address):
        loop = asyncio.get_event_loop()
        html_tree = loop.run_until_complete(self.make_request_to_get_summary_reviews(hname, address))
        return html_tree

    ##################################

    async def get_sidebar_content_block(self, html_tree):
        try:
            block = html_tree.xpath('//div[@id="rhs_block"]/h1[@class="bNg8Rb"]/text()')
            return block
        except NoSuchElementException as err:
            print("{}".format(err))
            return None
        except AttributeError as err:
            print("{}".format(err))
            pass

    async def get_summary_review_names(self, html_tree):
        try:
            summary_review_names = html_tree.xpath('//div[@class="NsRfAb XMibRe"]/div[@class="jlBtR"]/span[@class="zSN9Zd"]/text()')
            return summary_review_names
        except NoSuchElementException as err:
            print("{}".format(err))
            return None
        except AttributeError as err:
            print("{}".format(err))
            pass

    async def get_summary_review_ratings(self, html_tree):
        try:
            summary_review_ratings = html_tree.xpath(
                '//div[@class="NsRfAb XMibRe"]/div[@class="jlBtR"]/span[@class="Y0jGr"]/span[@class="rtng"]/text()')
            return summary_review_ratings
        except NoSuchElementException as err:
            print("{}".format(err))
            return None
        except AttributeError as err:
            print("{}".format(err))
            pass

    async def get_summary_review_texts(self, html_tree):
        try:
            row_texts = html_tree.xpath(
                '//div[@class="NsRfAb XMibRe"]/div[@class="jlBtR"]/div/span/text()')
            row = '__'.join(row_texts)
            rrow = row.replace("__·__", " · ")
            summary_review_texts = rrow.split("__")
            return summary_review_texts
        except NoSuchElementException as err:
            print("{}".format(err))
            return None
        except AttributeError as err:
            print("{}".format(err))
            pass

    # seventh set of tasks
    def seventh_task(self, html_tree):
        try:
            loop = asyncio.get_event_loop()
            block = loop.run_until_complete(self.get_sidebar_content_block(html_tree))
            return block
        except NoSuchElementException as err:
            print("{}".format(err))
            return None

    ##################################

    # eightth set of tasks
    def eightth_set_of_tasks(self, html_tree):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(self.get_summary_review_names(html_tree)),
            loop.create_task(self.get_summary_review_ratings(html_tree)),
            loop.create_task(self.get_summary_review_texts(html_tree)),
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

        summary_review_names = tasks[0].result()
        summary_review_ratings = tasks[1].result()
        summary_review_texts = tasks[2].result()

        return (summary_review_names, summary_review_ratings, summary_review_texts)

    ##################################

    def get_current_page_link(self, current_start_url):
        self.driver.get(current_start_url)

    def next_page_urls(self):
        time.sleep(2)
        try:
            html = self.driver.find_element_by_class_name('I8pMJe')
            html.send_keys(Keys.END)
        except NoSuchElementException:
            pass
        next_page_urls = self.driver.find_elements_by_xpath('//div[@class="s0qrvf"]/div[@class="vpy23b"]/div')
        return next_page_urls

    def next_page_url(self):
        time.sleep(5)
        html = self.driver.find_element_by_class_name('I8pMJe')
        html.send_keys(Keys.END)
        next_page_url = self.driver.find_element_by_xpath('//*[contains(text(), "U26fgb O0WRkf oG5Srb C0oVfc dihY6c sTz3p Avp8xd mOUdJ M9Bg4d")]')
        return next_page_url

    def next_as_next(self):
        html = self.driver.find_element_by_class_name('I8pMJe')
        html.send_keys(Keys.END)
        # time.sleep(2)
        next_as_next = self.driver.find_element_by_xpath('//div[@class="s0qrvf"]/div[@class="vpy23b"]/div/content/span[@class="RveJvd snByac"]').text
        return next_as_next

    def how_many(self):
        how_many = self.driver.find_element_by_class_name('lUZ35').text
        if '- 12' in how_many:
            divide_by = 12
        if '- 18' in how_many:
            divide_by = 18
        h_value_str = how_many.split("of ")
        h_value = int(h_value_str[-1].replace(",", ""))
        how_many_times = round(h_value / divide_by) + 1
        return how_many_times

    ###################################

    # check_for_hotel_id
    def check_for_hotel_id(self, hname):
        loop = asyncio.get_event_loop()
        hid = loop.run_until_complete(self.check_if_hotel_name_is_in_db(hname))
        print("HID: {}".format(hid))
        return hid

    # tenth task
    def add_to_hotel_table(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(newhotel.insert_hotel_to_db(adds, hname, website, direction, rating, reviews_count,
                                                            reviews_rating, address, phone, short_review, description))
        print("No HID, added new hotel to hotel table")

    ##################################

    # insert_location_overview
    def insert_location_overview(self, location_overview_text, hid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(location_highlights.insert_location_overview(
            location_overview_text, hid))
        print("added location_overview_text to location_overview table")

    # insert_location_score
    def insert_location_score(self, score_rate, score_text, hid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(location_highlights.insert_location_score(
            score_rate, score_text, hid))
        print("added score_rate, score_text, hid to location_score table")

    # insert_location_thing_to_do
    def insert_location_thing_to_do(self, location_thing_name, location_thing_text,
                                    location_thing_review_rate, location_thing_star_score,
                                    location_thing_distance, location_thing_img, hid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(location_thingstodo.insert_location_thing_to_do(
            location_thing_name, location_thing_text,
            location_thing_review_rate, location_thing_star_score,
            location_thing_distance, location_thing_img, hid))
        print("added score_rate, score_text, hid to location_thing_to_do table")

    # insert_location_getting_around
    def insert_location_getting_around(self, location_around_name, location_around_type_text, hid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(location_getting_around.insert_location_getting_around(
            location_around_name, location_around_type_text, hid))
        print("added location_around_name, location_around_type_text, hid to location_getting_around table")

    ##################################

    # insert_thing
    def insert_thing(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(nearby_things_to_do.insert_thing(
            thing_name, thing_distance_car, thing_distance_walk,
            thing_distance_bus, thing_img_link, hid))
        print("Added new thing to nearby_things_to_do table")

    ##################################

    # insert_to nearby_transit_stops table
    def insert_transit_stop(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(nearby_transit_stops.insert_transit_stop(
            stop_name, stop_type, stop_distance, hid))
        print("Added transit_stop to nearby_transit_stops table")

    ##################################

    # insert_airport
    def insert_airport(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(nearby_airports.insert_airport(
            airport_name, airport_distance_car, airport_distance_bus, hid))
        print("Added airport to nearby_airports table")

    ##################################

    # insert_nearby_hotel
    def insert_nearby_hotel(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_nearby_hotels.insert_nearby_hotel(
            hotel_name, hotel_img_link, hotel_star_rate,
            hotel_sum_reviews, hotel_about, hotel_distance, hid))
        print("Added new hotel to nearby_hotels table")

    ##################################

    # insert_rating_by_traveler_type
    def insert_rating_by_traveler_type(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(hreviews.insert_rating_by_traveler_type(
            type_name, type_rate, type_img_url, hid))
        print("Added new rating to rating_by_traveler_type table")

    ##################################

    # insert_travel_site_review
    def insert_travel_site_review(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(hreviews.insert_travel_site_review(
            site_name, site_rate, site_img_url, hid))
        print("Added new review rates to travel_site_review table")

    ##################################

    # insert_review
    def insert_review(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(hreviews.insert_review(
            review_author_name, review_timestamp,
            review_rating, review_text, review_img_url, hid))
        print("Added new review to reviews table")

    ##################################

    # select_amenity
    def select_amenity(self, amenity):
        loop = asyncio.get_event_loop()
        aid = loop.run_until_complete(amenities.select_amenity(amenity))
        print("AID: {}".format(aid))
        return aid

    # insert_amenity
    def insert_amenity(self, amenity):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(amenities.insert_amenity(amenity))
        print("No AID, added new amenity to amenities table")

    # thirteenth task
    def insert_to_hotel_amenities_table(self, hid, aid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(amenities.insert_to_hotel_amenities_table(hid, aid))
        print("Done insert_to_hotel_amenities_table where hid : {} and aid : {}".format(hid, aid))

    ##################################

    # select_accessibility
    def select_accessibility(self, accessibility):
        loop = asyncio.get_event_loop()
        acid = loop.run_until_complete(accessibilities.select_accessibility(accessibility))
        print("ACID: {}".format(acid))
        return acid

    # insert_accessibility
    def insert_accessibility(self, accessibility):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(accessibilities.insert_accessibility(accessibility))
        print("No ACID, added new accessibility to accessibilities table")

    # insert_to_hotel_accessibilities_table
    def insert_to_hotel_accessibilities_table(self, hid, acid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(accessibilities.insert_to_hotel_accessibilities_table(hid, acid))
        print("Done insert_to_hotel_accessibilities_table where hid : {} and acid : {}".format(hid, acid))

    ##################################

    # select_activity
    def select_activity(self, activity):
        loop = asyncio.get_event_loop()
        actid = loop.run_until_complete(activities.select_activity(activity))
        print("ACTID: {}".format(actid))
        return actid

    # insert_activity
    def insert_activity(self, activity):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(activities.insert_activity(activity))
        print("No ACTID, added new activity to activities table")

    # insert_to_hotel_activities_table
    def insert_to_hotel_activities_table(self, hid, actid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(activities.insert_to_hotel_activities_table(hid, actid))
        print("Done insert_to_hotel_activities_table where hid : {} and actid : {}".format(hid, actid))

    ##################################

    # select_crowd
    def select_crowd(self, crowd):
        loop = asyncio.get_event_loop()
        crid = loop.run_until_complete(crowds.select_crowd(crowd))
        print("CRID: {}".format(crid))
        return crid

    # insert_crowd
    def insert_crowd(self, crowd):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(crowds.insert_crowd(crowd))
        print("No CRID, added new crowd to crowds table")

    # insert_to_hotel_crowds_table
    def insert_to_hotel_crowds_table(self, hid, crid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(crowds.insert_to_hotel_crowds_table(hid, crid))
        print("Done insert_to_hotel_crowds_table where hid : {} and crid : {}".format(hid, crid))

    ##################################

    # select_lodging_option
    def select_lodging_option(self, lodging_option):
        loop = asyncio.get_event_loop()
        loid = loop.run_until_complete(lodging_options.select_lodging_option(lodging_option))
        print("LOID: {}".format(loid))
        return loid

    # insert_lodging_option
    def insert_lodging_option(self, lodging_option):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(lodging_options.insert_lodging_option(lodging_option))
        print("No LOID, added new lodging_option to lodging_options table")

    # insert_to_hotel_lodging_options_table
    def insert_to_hotel_lodging_options_table(self, hid, loid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(lodging_options.insert_to_hotel_lodging_options_table(hid, loid))
        print("Done insert_to_hotel_lodging_options_table where hid : {} and loid : {}".format(hid, loid))

    ##################################

    # select_offering
    def select_offering(self, offering):
        loop = asyncio.get_event_loop()
        ofid = loop.run_until_complete(offerings.select_offering(offering))
        print("OFID: {}".format(ofid))
        return ofid

    # insert_offering
    def insert_offering(self, offering):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(offerings.insert_offering(offering))
        print("No OFID, added new offering to offerings table")

    # insert_to_hotel_offerings_table
    def insert_to_hotel_offerings_table(self, hid, ofid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(offerings.insert_to_hotel_offerings_table(hid, ofid))
        print("Done insert_to_hotel_offerings_table where hid : {} and ofid : {}".format(hid, ofid))

    ##################################

    # select_payment
    def select_payment(self, payment):
        loop = asyncio.get_event_loop()
        pmid = loop.run_until_complete(payments.select_payment(payment))
        print("PMID: {}".format(pmid))
        return pmid

    # insert_payment
    def insert_payment(self, payment):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(payments.insert_payment(payment))
        print("No PMID, added new payment to payments table")

    # insert_to_hotel_payments_table
    def insert_to_hotel_payments_table(self, hid, pmid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(payments.insert_to_hotel_payments_table(hid, pmid))
        print("Done insert_to_hotel_payments_table where hid : {} and pmid : {}".format(hid, pmid))

    ##################################

    # select_planning
    def select_planning(self, planning):
        loop = asyncio.get_event_loop()
        plid = loop.run_until_complete(plannings.select_planning(planning))
        print("PLID: {}".format(plid))
        return plid

    # insert_planning
    def insert_planning(self, planning):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(plannings.insert_planning(planning))
        print("No PLID, added new planning to plannings table")

    # insert_to_hotel_plannings_table
    def insert_to_hotel_plannings_table(self, hid, pmid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(plannings.insert_to_hotel_plannings_table(hid, plid))
        print("Done insert_to_hotel_plannings_table where hid : {} and plid : {}".format(hid, plid))

    ##################################

    # select_highlight
    def select_highlight(self, highlight_text):
        loop = asyncio.get_event_loop()
        hlid = loop.run_until_complete(_highlights.select_highlight(highlight_text))
        print("HLID: {}".format(hlid))
        return hlid

    # insert_highlight
    def insert_highlight(self, highlight_img, highlight_text):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_highlights.insert_highlight(highlight_img, highlight_text))
        print("No HLID, added new highlight to highlights table")

    # insert_to_hotel_highlights_table
    def insert_to_hotel_highlights_table(self, hid, hlid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_highlights.insert_to_hotel_highlights_table(hid, hlid))
        print("Done insert_to_hotel_highlights_table where hid : {} and hlid : {}".format(hid, hlid))

    ##################################

    # select_fhighlight
    def select_fhighlight(self, fhighlight):
        loop = asyncio.get_event_loop()
        fhlid = loop.run_until_complete(fhighlights.select_fhighlight(fhighlight))
        print("FHLID: {}".format(fhlid))
        return fhlid

    # insert_fhighlight
    def insert_fhighlight(self, fhighlight):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fhighlights.insert_fhighlight(fhighlight))
        print("No FHLID, added new fhighlight to fhighlights table")

    # insert_to_hotel_fhighlights_table
    def insert_to_hotel_fhighlights_table(self, hid, fhlid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fhighlights.insert_to_hotel_fhighlights_table(hid, fhlid))
        print("Done insert_to_hotel_fhighlights_table where hid : {} and fhlid : {}".format(hid, fhlid))

    ##################################

    # select_srid
    def select_srid(self, stext):
        loop = asyncio.get_event_loop()
        srid = loop.run_until_complete(hreviews.select_srid(stext))
        print("SRID: {}".format(srid))
        return srid

    # insert_srid
    def insert_srid(self, scat, srating, stext):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(hreviews.insert_srid(scat, srating, stext))
        print("No SRID, added new summary_review to summary_reviews table")

    # insert_to_hotel_summary_review_table
    def insert_to_hotel_summary_review_table(self, hid, srid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(hreviews.insert_to_hotel_summary_review_table(hid, srid))
        print("Done insert_to_hotel_summary_review_table where hid : {} and srid : {}".format(hid, srid))

    ##################################

    # select_url
    def select_url(self, mapped_url):
        loop = asyncio.get_event_loop()
        uid = loop.run_until_complete(mapped_urls.select_url(mapped_url))
        print("UID: {}".format(uid))
        return uid

    # insert_url
    def insert_url(self, mapped_url):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(mapped_urls.insert_url(mapped_url))
        print("No UID, added new url to mapped_urls table")

    # insert_to_hotel_mapped_url
    def insert_to_hotel_mapped_url(self, hid, uid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(mapped_urls.insert_to_hotel_mapped_url(hid, uid))
        print("Done insert_to_hotel_mapped_url where hid : {} and uid : {}".format(hid, uid))

    ##################################

    # select_category_id
    def select_category_id(self, img_category):
        loop = asyncio.get_event_loop()
        caid = loop.run_until_complete(photos.select_category_id(img_category))
        print("CAID: {}".format(caid))
        return caid

    # insert_image url
    def insert_photo(self, photo_url, hid, caid, soid, foid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(photos.insert_photo(photo_url, hid, caid, soid, foid))
        print(f"Added new photo to photos table")

    # select_source_id
    def select_source_id(self, img_source):
        loop = asyncio.get_event_loop()
        soid = loop.run_until_complete(photos.select_source_id(img_source))
        print("SOID: {}".format(soid))
        return soid

    # check_source
    def check_source(self, photo_url):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(photos.check_source(photo_url))
        return result

    # update_source
    def update_source(self, soid, hid, photo_url):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(photos.update_source(soid, hid, photo_url))
        print(f"Updated source_id to photo")
        return result

    # select_format_id
    def select_format_id(self, img_format):
        loop = asyncio.get_event_loop()
        foid = loop.run_until_complete(photos.select_format_id(img_format))
        print("FOID: {}".format(foid))
        return foid

    # update_format
    def update_format(self, foid, hid, photo_url):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(photos.update_format(foid, hid, photo_url))
        print(f"Updated format_id to photo")

    # check_source
    def check_format(self, photo_url):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(photos.check_format(photo_url))
        return result

    def proxy_connector(self, c_proxy):
        connector = SocksConnector.from_url(
            f'socks5://{c_proxy[0]}:{c_proxy[1]}', verify_ssl=False)
        return connector

    def pconnector(self, current_proxy):
        connector = SocksConnector.from_url(current_proxy, verify_ssl=False)
        return connector

    ##################################


if __name__ == "__main__":
    g = GoogleSearchHotels()
    queries = set(g.get_q_list())
    print(f"Queries: {queries}")
    for q in queries:
        google_query = g.making_google_query(q)
        g.google_request(google_query)
        check_button = g.check_button()
        if check_button:
            g.del_from_q_list(q)
            continue
        how_many = 1000
        print(f"all hotels: {how_many}")
        try:
            g.click_in_google()
        except NoSuchElementException as err:
            print(f"No block1 to click, go next try:")
            try:
                g.click_in_google1()
            except NoSuchElementException as err:
                print(f"No block2 to click, break:")
                g.del_from_q_list(q)
                continue
        for i in range(how_many):
            try:
                objs_names = g.third_set_of_tasks()
                try:
                    if objs_names == []:
                        print(f"objs_names == 0 :: break")
                        break
                    if objs_names[1] == '':
                        print(f"objs_names == '' :: break")
                        break
                except IndexError:
                    print(f"objs_names == 0 :: break")
                    break
                for i in objs_names:
                    qu.put(i)
                get_back_url = g.now_get_current_url()
                while not qu.empty():
                    obj, hname = qu.get()
                    all_db_names = g.fourth_task()
                    if hname in all_db_names:
                        print("BYPASS : {}".format(hname))
                        continue
                    if hname == 0:
                        print(f"No hnames, deleting q: {q}")
                        g.del_from_q_list(q)
                        break

                    t0 = time.time()
                    g.click_on_obj(obj)
                    time.sleep(2)
                    nearby_hotels = g.get_hotel_nearby_hotels()
                    print()
                    pprint(f"Nearby Hotels: {nearby_hotels}")
                    print()
                    nearby_hotel_imgs = g.get_hotel_nearby_hotel_imgs()
                    print()
                    pprint(f"Nearby Hotel IMGS: {nearby_hotel_imgs}")
                    print()
                    try:
                        nearby_objs, nearby_imgs = g.get_hotel_nearby()
                        print()
                        pprint(f"Nearby_Imgs: {nearby_imgs}")
                        print()
                        things_to_do = nearby_objs[0]
                        for thing in things_to_do:
                            thing[1] = thing[1].replace("\ue530", "Bus").replace("\ue559", "Car").replace("\ue536", "Walking").replace("\ue533", "Subway")
                            thing[2] = thing[2].replace("\ue530", "Bus").replace("\ue559", "Car").replace("\ue536", "Walking").replace("\ue533", "Subway")
                        transit_stops = nearby_objs[1]
                        for stop in transit_stops:
                            stop[1] = stop[1].replace(
                                "\ue536 ", "").replace("\ue570 ", "").replace("\ue530 ", "").replace("\ue571 ", "").replace("\ue533 ", "")
                            stop[2] = stop[2].replace(
                                "\ue536 ", "").replace("\ue570 ", "").replace("\ue530 ", "").replace("\ue571 ", "").replace("\ue533 ", "")
                        airports = nearby_objs[2]
                        for airport in airports:
                            airport[1] = airport[1].replace(
                                "\ue559", "Car").replace("\ue530", "Bus").replace("\ue536", "Walking").replace("\ue533", "Subway")
                            airport[2] = airport[2].replace(
                                "\ue559", "Car").replace("\ue530", "Bus").replace("\ue536", "Walking").replace("\ue533", "Subway")
                        print()
                        pprint(f"Things_to_do: {things_to_do}")
                        print()
                        pprint(f"Transit_stops: {transit_stops}")
                        print()
                        pprint(f"Airports: {airports}")
                        print()
                    except TypeError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    except IndexError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    try:
                        hotel = g.fifth_set_of_tasks()
                    except TypeError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    pprint("Hotel Data: {}".format(hotel))
                    (adds, name, website, direction, rating, reviews_count,
                        reviews_rating, address, phone, short_review) = hotel

                    g.open_description()
                    description, highlights_imgs, highlights_texts, facilities = g.description_tasks()
                    print()
                    pprint(f"Hotel DESCRIPTION: {description}")
                    print()
                    highlights = tuple(zip(highlights_imgs, highlights_texts))
                    pprint(f"Hotel highlights: {highlights}")
                    print()
                    fa_names = ["Amenities", "Accessibility", "Activities", "Crowd",
                                "Lodging options", "Offerings", "Payments", "Planning", "Highlights"]
                    facilities1 = []
                    for fa_name in fa_names:
                        for key, value in facilities.items():
                            if fa_name == key:
                                facility = (fa_name, value)
                                facilities1.append(facility)
                    myfacilities = tuple(facilities1)

                    pprint(f"Hotel myfacilities: {myfacilities}")
                    print()

                    g.open_location()
                    try:
                        location_overview_text, location_score = g.get_location_highlights()
                        print()
                        pprint(f"Location_overview: {location_overview_text}")
                        pprint(f"Location_Score: {location_score}")
                        print()
                    except TypeError as err:
                        print(f"No location overview: {err}")
                        pass
                    except IndexError as err:
                        print(f"No location overview: {err}")
                        pass
                    except NameError as err:
                        print(f"No location overview: {err}")
                        pass
                    try:
                        g.get_to_location_things_to_do()
                        location_things_to_do, location_things_imgs = g.get_location_things_to_do()
                        print()
                        pprint("Location_things_to_do: {}".format(location_things_to_do))
                        print()
                    except TypeError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    except IndexError as err:
                        print(f"No location to do: {err}")
                        pass
                    try:
                        g.get_to_location_getting_around()
                        getting_arounds = g.get_location_getting_around()
                        print()
                        pprint("Location_getting_arounds: {}".format(getting_arounds))
                        print()
                    except TypeError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    except IndexError as err:
                        print(f"No location arounds: {err}")
                        pass
                    g.open_reviews()
                    (reviews_on_other_sites, reviews_imgs, type_names, type_rates, ratings_imgs,
                        reviews_list, ten_reviews_imgs) = g.reviews_page_tasks()
                    print()
                    pprint("Reviews on other sites: {}".format(reviews_on_other_sites, reviews_imgs))
                    print()
                    pprint("Ratings by traveler type: {}".format(type_names, type_rates, ratings_imgs))
                    print()
                    pprint("Ten reviews: {}".format(reviews_list, ten_reviews_imgs))
                    print()

                    # html_tree = g.six_task(hname, address)
                    # block = g.seventh_task(html_tree)
                    # (summary_review_names, summary_review_ratings,
                    #     summary_review_texts) = g.eightth_set_of_tasks(html_tree)
                    # try:
                    #     rev = tuple(zip(summary_review_names, summary_review_ratings, summary_review_texts))
                    #     pprint(f"Summary review: {rev}")
                    #     print()
                    # except TypeError as err:
                    #     print(f"It happend: {err}")
                    #     pass

                    # if need price links
                    g.open_prices()
                    links_to_map = g.async_get_hotel_links_to_map()
                    links_set = set(links_to_map)
                    redirect_urls = []
                    for link in links_set:
                        try:
                            url = g.get_redirects(link)
                            redirect_urls.append(url)
                        except asyncio.TimeoutError as e:
                            print(f"TIMEOUT: {str(e)}")
                            continue
                        except ServerDisconnectedError as e:
                            print("Server disconnected")
                            continue
                        except ClientConnectorError as e:
                            print(f"ClientConnectorError: {str(e)}")
                            continue
                    print(f"Price URLS: {redirect_urls}")
                    print(f"HNAME: {hname}")

                    ####################################################
                    # start of db tasks
                    hid = g.check_for_hotel_id(str(hname).replace("'", "\'"))
                    if not hid:
                        g.add_to_hotel_table(
                            adds, hname, website, direction, rating, reviews_count,
                            reviews_rating, address, phone, short_review, description)
                        hid = g.check_for_hotel_id(str(hname).replace("'", "\'"))

                    try:
                        g.insert_location_overview(location_overview_text, hid)
                    except TypeError as err:
                        print(f"No location overview: {err}")
                        pass
                    except IndexError as err:
                        print(f"No location overview: {err}")
                        pass
                    except NameError as err:
                        print(f"No location overview: {err}")
                        location_overview_text = None
                        g.insert_location_overview(location_overview_text, hid)
                    try:
                        for score_rate, score_text in location_score:
                            if len(score_rate) > 15:
                                score_rate = None
                                score_text = None
                                g.insert_location_score(score_rate, score_text, hid)
                            else:
                                g.insert_location_score(score_rate, score_text, hid)
                    except ValueError as err:
                        print("{}".format(err))
                        pass
                    except TypeError as err:
                        print("{}".format(err))
                        pass
                    except IndexError as err:
                        print("{}".format(err))
                        pass
                    except NameError as err:
                        print("{}".format(err))
                        pass
                    try:
                        for obj in location_things_to_do:
                            for l_img in location_things_imgs:
                                location_thing_img = l_img
                                location_thing_name = obj[0]
                                location_thing_text = obj[1]
                                location_thing_review_rate = obj[2]
                                location_thing_star_score = obj[3]
                                location_thing_distance = obj[4].replace(
                                    '\ue559', 'Distance by car').replace(
                                    '\ue530', 'Distance by bus').replace(
                                    '\ue536', 'Distance walking')

                            g.insert_location_thing_to_do(
                                location_thing_name, location_thing_text,
                                location_thing_review_rate, location_thing_star_score,
                                location_thing_distance, location_thing_img, hid)
                    except ValueError as err:
                        print("{}".format(err))
                        pass
                    except TypeError as err:
                        print("{}".format(err))
                        pass
                    except IndexError as err:
                        print("{}".format(err))
                        pass
                    try:
                        for location_around_name, around_types in getting_arounds:
                            for location_around_type_text in around_types:
                                g.insert_location_getting_around(
                                    location_around_name, location_around_type_text, hid)
                    except ValueError as err:
                        print("{}".format(err))
                        pass
                    except TypeError as err:
                        print("{}".format(err))
                        pass
                    except NameError as err:
                        print("{}".format(err))
                        pass

                    try:
                        for thing, img in zip(things_to_do, nearby_imgs):
                            thing_name = thing[0]
                            thing_img_link = img
                            if 'Car' in thing[1]:
                                thing_distance_car = thing[1]
                            elif 'Car' in thing[2]:
                                thing_distance_car = thing[2]
                            else:
                                thing_distance_car = None
                            if 'Walking' in thing[1]:
                                thing_distance_walk = thing[1]
                            elif 'Walking' in thing[2]:
                                thing_distance_walk = thing[2]
                            else:
                                thing_distance_walk = None
                            if 'Bus' in thing[1]:
                                thing_distance_bus = thing[1]
                            elif 'Bus' in thing[2]:
                                thing_distance_bus = thing[2]
                            else:
                                thing_distance_bus = None
                            g.insert_thing(
                                thing_name, thing_distance_car,
                                thing_distance_walk, thing_distance_bus,
                                thing_img_link, hid)

                        for stop in transit_stops:
                            stop_name = stop[0]
                            stop_type = stop[1]
                            stop_distance = stop[2]
                            g.insert_transit_stop(
                                stop_name, stop_type, stop_distance, hid)

                        for airport in airports:
                            airport_name = airport[0]
                            if 'Car' in airport[1]:
                                airport_distance_car = airport[1]
                            elif 'Car' in airport[2]:
                                airport_distance_car = airport[2]
                            else:
                                airport_distance_car = None
                            if 'Bus' in airport[1]:
                                airport_distance_bus = airport[1]
                            elif 'Bus' in airport[2]:
                                airport_distance_bus = airport[2]
                            else:
                                airport_distance_bus = None
                            g.insert_airport(
                                airport_name, airport_distance_car,
                                airport_distance_bus, hid)
                    except ValueError as err:
                        print("{}".format(err))
                        pass
                    except TypeError as err:
                        print("{}".format(err))
                        pass
                    except NameError as err:
                        print("{}".format(err))
                        pass
                    except IndexError as err:
                        print(f"No nearbyes: {err}")
                        pass
                    try:
                        for nearby_hotel, hotel_img in zip(nearby_hotels, nearby_hotel_imgs):
                            print(f"NEARBY HOTEL: {nearby_hotel}")
                            while '\ue838':
                                try:
                                    nearby_hotel.remove('\ue838')
                                except ValueError:
                                    break
                            try:
                                if nearby_hotel[-2].startswith("("):
                                    nearby_hotel.insert(3, "-")
                            except IndexError:
                                pass
                            try:
                                hotel_name = nearby_hotel[0]
                                hotel_img_link = hotel_img
                                hotel_star_rate = nearby_hotel[1]
                                hotel_sum_reviews = nearby_hotel[2]
                                hotel_about = nearby_hotel[3]
                                hotel_distance = nearby_hotel[4]
                            except IndexError as err:
                                print(f"NO NEARBY HOTEL: {err}")
                                hotel_name = '-'
                                hotel_img_link = '-'
                                hotel_star_rate = '-'
                                hotel_sum_reviews = '-'
                                hotel_about = '-'
                                hotel_distance = '-'
                            g.insert_nearby_hotel(
                                hotel_name, hotel_img_link, hotel_star_rate,
                                hotel_sum_reviews, hotel_about, hotel_distance, hid)

                        for highlight_img, highlight_text in highlights:
                            hlid = g.select_highlight(highlight_text)
                            if not hlid:
                                g.insert_highlight(highlight_img, highlight_text)
                                hlid = g.select_highlight(highlight_text)
                            g.insert_to_hotel_highlights_table(hid, hlid)

                        for facility in myfacilities:
                            if facility[0] == "Amenities":
                                for amenity in facility[1]:
                                    aid = g.select_amenity(amenity)
                                    if not aid:
                                        print("No AID : inserting to DB")
                                        g.insert_amenity(amenity)
                                        aid = g.select_amenity(amenity)
                                    g.insert_to_hotel_amenities_table(hid, aid)
                            elif facility[0] == "Accessibility":
                                for accessibility in facility[1]:
                                    acid = g.select_accessibility(accessibility)
                                    if not acid:
                                        print("No ACID : inserting to DB")
                                        g.insert_accessibility(accessibility)
                                        acid = g.select_accessibility(accessibility)
                                    g.insert_to_hotel_accessibilities_table(hid, acid)
                            elif facility[0] == "Activities":
                                for activity in facility[1]:
                                    actid = g.select_activity(activity)
                                    if not actid:
                                        print("No ACTID : inserting to DB")
                                        g.insert_activity(activity)
                                        actid = g.select_activity(activity)
                                    g.insert_to_hotel_activities_table(hid, actid)
                            elif facility[0] == "Crowd":
                                for crowd in facility[1]:
                                    crid = g.select_crowd(crowd)
                                    if not crid:
                                        print("No CRID : inserting to DB")
                                        g.insert_crowd(crowd)
                                        crid = g.select_crowd(crowd)
                                    g.insert_to_hotel_crowds_table(hid, crid)
                            elif facility[0] == "Lodging options":
                                for lodging_option in facility[1]:
                                    loid = g.select_lodging_option(lodging_option)
                                    if not loid:
                                        print("No LOID : inserting to DB")
                                        g.insert_lodging_option(lodging_option)
                                        loid = g.select_lodging_option(lodging_option)
                                    g.insert_to_hotel_lodging_options_table(hid, loid)
                            elif facility[0] == "Offerings":
                                for offering in facility[1]:
                                    ofid = g.select_offering(offering)
                                    if not ofid:
                                        print("No ofid : inserting to DB")
                                        g.insert_offering(offering)
                                        ofid = g.select_offering(offering)
                                    g.insert_to_hotel_offerings_table(hid, ofid)
                            elif facility[0] == "Payments":
                                for payment in facility[1]:
                                    pmid = g.select_payment(payment)
                                    if not pmid:
                                        print("No PMID : inserting to DB")
                                        g.insert_payment(payment)
                                        pmid = g.select_payment(payment)
                                    g.insert_to_hotel_payments_table(hid, pmid)
                            elif facility[0] == "Planning":
                                for planning in facility[1]:
                                    plid = g.select_planning(planning)
                                    if not plid:
                                        print("No PLID : inserting to DB")
                                        g.insert_planning(planning)
                                        plid = g.select_planning(planning)
                                    g.insert_to_hotel_plannings_table(hid, plid)

                            elif facility[0] == "Highlights":
                                for fhighlight in facility[1]:
                                    fhlid = g.select_fhighlight(fhighlight)
                                    if not fhlid:
                                        print("No PLID : inserting to DB")
                                        g.insert_fhighlight(fhighlight)
                                        fhlid = g.select_fhighlight(fhighlight)
                                    g.insert_to_hotel_fhighlights_table(hid, fhlid)
                    except ValueError as err:
                        print("{}".format(err))
                        pass
                    except TypeError as err:
                        print("{}".format(err))
                        pass
                    except NameError as err:
                        print("{}".format(err))
                        pass

                    try:
                        for rev, img in zip(reviews_on_other_sites, reviews_imgs):
                            site_name = rev[1]
                            site_rate = rev[0]
                            site_img_url = img
                            g.insert_travel_site_review(
                                site_name, site_rate, site_img_url, hid)
                    except IndexError as err:
                        print(f"Out of range: {err}")
                        pass
                    except TypeError as err:
                        print(f"NO items: {err}")
                        pass

                    try:
                        for type_name, type_rate, rate_img in zip(type_names,
                                                                  type_rates,
                                                                  ratings_imgs):
                            type_img_url = rate_img
                            g.insert_rating_by_traveler_type(
                                type_name, type_rate, type_img_url, hid)
                    except TypeError as err:
                        print(f"NO: {err}")
                        pass
                    try:
                        for review, review_img in zip(reviews_list, ten_reviews_imgs):
                            review_author_name = review[0]
                            review_timestamp = review[1]
                            review_rating = review[2]
                            review_text = review[3]
                            review_img_url = review_img
                            if len(review_rating) > 35:
                                review_author_name = None
                                review_timestamp = None
                                review_rating = None
                                review_text = None
                                review_img_url = None
                                g.insert_review(
                                review_author_name, review_timestamp,
                                review_rating, review_text, review_img_url, hid)
                            else:
                                g.insert_review(
                                    review_author_name, review_timestamp,
                                    review_rating, review_text, review_img_url, hid)
                    except TypeError as err:
                        print(f"NO: {err}")
                        pass
                    except IndexError as err:
                        print(f"NO: {err}")
                        pass

                    # try:
                    #     for scat, srating, stext in tuple(zip(summary_review_names,
                    #                                           summary_review_ratings,
                    #                                           summary_review_texts)):
                    #         print(f"S_Review: {scat, srating, stext}")
                    #         srid = g.select_srid(stext)
                    #         if not srid:
                    #             g.insert_srid(scat, srating, stext)
                    #             srid = g.select_srid(stext)
                    #         g.insert_to_hotel_summary_review_table(hid, srid)
                    # except TypeError as err:
                    #     print(f"NO: {err}")
                    #     pass
                    # except IndexError as err:
                    #     print(f"NO: {err}")
                    #     pass

                    # if need to get mapped urls (Google Adds links/redirects)
                    try:
                        for mapped_url in redirect_urls:
                            uid = g.select_url(str(mapped_url))
                            if not uid:
                                g.insert_url(str(mapped_url))
                                uid = g.select_url(str(mapped_url))
                            else:
                                print(f"UniqueError: {uid} is here. Passing...")
                                pass
                            g.insert_to_hotel_mapped_url(hid, uid)
                    except TypeError as err:
                        print(f"TypeError: {err}")
                        pass
                    except IndexError as err:
                        print(f"IndexError: {err}")
                        pass
                    except asyncpg.UniqueViolationError as err:
                        print(f"UniqueViolationError: {err}")
                        pass

                    g.open_photos()
                    all_img_urls = set()
                    cats = []
                    categories = g.img_category_tasks()
                    print(f"categories: {categories}")
                    for category in categories:
                        cat = g.img_category_first_task_set()
                        print(f"+Categories: {cat}")
                        for c, v in cat.items():
                            if category not in c:
                                continue
                            elif category in c:
                                print(f"Current {category} is in {c}")
                                v.click()
                                img_category, images = g.img_category_second_task_set()
                                print(f"IMGS: {len(images)}")
                                img_c = str(img_category).replace("['", "").replace("']", "")
                                caid = g.select_category_id(img_c)
                                photo_urls = set(images)
                                print(f"IMG CAID: {caid}")
                                print(f"IMG PHOTO URL: {len(photo_urls)}")
                                if img_c == 'Ausstattung':
                                    acaid = caid
                                    amenities = photo_urls
                                    print(f"amenities: {amenities}")
                                    for url in amenities:
                                        ext_id = (acaid, url)
                                        cats.append(ext_id)
                                    all_img_urls = all_img_urls | amenities
                                if img_c == 'Zimmer':
                                    rcaid = caid
                                    rooms = photo_urls
                                    print(f"rooms: {rooms}")
                                    for url in rooms:
                                        ext_id = (rcaid, url)
                                        cats.append(ext_id)
                                    all_img_urls = all_img_urls | rooms
                                if img_c == 'Außenbereich':
                                    ecaid = caid
                                    exterior = photo_urls
                                    for url in exterior:
                                        ext_id = (ecaid, url)
                                        cats.append(ext_id)
                                    all_img_urls = all_img_urls | exterior
                                if img_c == 'Essen & Trinken':
                                    fcaid = caid
                                    food_drink = photo_urls
                                    for url in food_drink:
                                        ext_id = (fcaid, url)
                                        cats.append(ext_id)
                                    all_img_urls = all_img_urls | food_drink
                                print("Need to open to get another category")
                                print(f"NOW")
                                g.img_category_pre_last_task()
                                print(f"Now HERE")
                        print("Need to close current category...")
                        g.img_category_last_task()

                    sours = []
                    sources = g.img_sources_tasks()
                    print(f"sources: {sources}")
                    for source in sources:
                        sour = g.img_sources_first_task_set()
                        print(f"+Sources: {sour}")
                        for s, v in sour.items():
                            if source not in s:
                                continue
                            elif source in s:
                                print(f"Current {source} is in {s}")
                                v.click()
                                img_source, images = g.img_source_second_task_set()
                                print(f"IMGS: {len(images)}")
                                img_s = str(img_source).replace("['", "").replace("']", "")
                                soid = g.select_source_id(img_s)
                                photo_urls = set(images)
                                print(f"IMG SOID: {soid}")
                                print(f"IMG PHOTO URL: {len(photo_urls)}")
                                if img_s == 'Von Gästen':
                                    vsoid = soid
                                    from_visitors = photo_urls
                                    for url in from_visitors:
                                        ext_id = (vsoid, url)
                                        sours.append(ext_id)
                                    all_img_urls = all_img_urls | from_visitors

                                if img_s == 'Vom Hotel':
                                    psoid = soid
                                    from_property = photo_urls
                                    for url in from_property:
                                        ext_id = (psoid, url)
                                        sours.append(ext_id)
                                    all_img_urls = all_img_urls | from_property
                                print("Need to open to get another sources category")
                                g.img_sources_pre_last_task()
                        print("Need to close current sources category...")
                        g.img_category_last_task()

                    forms = []
                    formats = g.img_formats_tasks()
                    print(f"formats: {formats}")
                    for iformat in formats:
                        iform = g.img_formats_first_task_set()
                        print(f"+Formats: {iform}")
                        for f, v in iform.items():
                            if iformat not in f:
                                continue
                            elif iformat in f:
                                print(f"Current {iformat} is in {f}")
                                v.click()
                                img_format, images = g.img_format_second_task_set()
                                print(f"IMGS: {len(images)}")
                                img_f = str(img_format).replace("['", "").replace("']", "")
                                foid = g.select_format_id(img_f)
                                photo_urls = set(images)
                                print(f"IMG FOID: {foid}")
                                print(f"IMG PHOTO URL: {len(photo_urls)}")
                                if img_f == '360°-Ansicht':
                                    vfoid = foid
                                    view = photo_urls
                                    for url in view:
                                        ext_id = (vfoid, url)
                                        forms.append(ext_id)
                                    all_img_urls = all_img_urls | view
                                if img_f == 'Fotos':
                                    pfoid = foid
                                    fphotos = photo_urls
                                    for url in fphotos:
                                        ext_id = (pfoid, url)
                                        forms.append(ext_id)
                                    all_img_urls = all_img_urls | fphotos
                                print("Need to open to get another formats category")
                                g.img_formats_pre_last_task()
                        print("Need to close current formats category...")
                        category_objs = g.img_category_last_task()
                        try:
                            if not category_objs[0]:
                                pass
                        except TypeError:
                            pass
                    try:
                        for url in all_img_urls:
                            insert_data = (url, hid)
                            if len(cats) != 0:
                                missed_cat_none = []
                                for i in cats:
                                    if url in i[1]:
                                        insert_data = insert_data + (i[0],)
                                        missed_cat_none.append(i[0])
                                        break
                                if len(missed_cat_none) == 0:
                                    insert_data = insert_data + (None,)
                            else:
                                insert_data = insert_data + (None,)
                            if len(sours) != 0:
                                missed_sours_none = []
                                for i in sours:
                                    if url in i[1]:
                                        insert_data = insert_data + (i[0],)
                                        missed_sours_none.append(i[0])
                                        break
                                if len(missed_sours_none) == 0:
                                    insert_data = insert_data + (None,)
                            else:
                                insert_data = insert_data + (None,)
                            if len(forms) != 0:
                                missed_forms_none = []
                                for i in forms:
                                    if url in i[1]:
                                        insert_data = insert_data + (i[0],)
                                        missed_forms_none.append(i[0])
                                        break
                                if len(missed_forms_none) == 0:
                                    insert_data = insert_data + (None,)
                            else:
                                insert_data = insert_data + (None,)
                            print(f"INSERT DATA: {insert_data}")
                            (photo_url, hid, caid, soid, foid) = insert_data
                            print(f"NEW: {(photo_url, hid, caid, soid, foid)}")
                            g.insert_photo(photo_url, hid, caid, soid, foid)
                        print(f"DONE INSERTING IMAGES")
                    except TypeError as err:
                        print(f"TypeError: {err}")
                    except NameError as err:
                        print(f"NameError: {err}")


                    g.click_to_get_back(get_back_url)
                    t1 = time.time()
                    print('Took', t1 - t0, 'seconds')

                try:
                    buts = g.next_page_urls()
                except NoSuchElementException:
                    print(f"No buts: {buts}")
                    break
                try:
                    g.button_close()
                except NoSuchElementException:
                    pass
                if len(buts) != 0:
                    if len(buts) == 2:
                        print(f"len buts: {len(buts)}")
                        buts[1].click()
                    if len(buts) == 1:
                        print(f"len buts: {len(buts)}")
                        next_as_next = g.next_as_next()
                        print(f"next_as_next: {next_as_next}")
                        if next_as_next.startswith('WEITER'):
                            buts[0].click()
                            time.sleep(3)
                        if next_as_next.endswith('ZURÜCK'):
                            print('No next page url, breaking loop')
                            break
                else:
                    break

            except ElementNotInteractableException as err:
                print("{}".format(err))
                g.reload()
                pass
            except StaleElementReferenceException as err:
                print("{}".format(err))
                pass
            except ElementClickInterceptedException as err:
                print("{}".format(err))
                pass
        print(f"All is fine")
        print(f"Deleting Q from QUERIES HERE {q}")
        g.del_from_q_list(q)
        continue
