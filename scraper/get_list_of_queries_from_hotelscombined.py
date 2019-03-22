import os
import random

from selenium import webdriver
from chrome_useragents import chrome

gecko_path = os.path.abspath(os.path.curdir) + '/geckodriver'
profile = webdriver.FirefoxProfile()
driver = webdriver.Firefox(firefox_profile=profile, executable_path=gecko_path)
driver.get('https://www.hotelscombined.com/Place/Austria.htm')
objs = driver.find_elements_by_xpath('//div[@class="hc_m_content"]/ul/li/a')
queries = [i.text for i in objs]
while '' in queries:
    queries.remove('')
with open(f"{os.path.abspath(os.path.curdir)}" + "/Austria.txt", "w") as f:
    for query in queries:
        f.write('"' + f'{query}' + '"' + ',' + '\n')
