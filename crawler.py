import json
import pprint
import time

import requests
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from travel_times import TravelTimes


def get_collection():
    client = MongoClient('localhost', 27017)
    db = client.apartment_db
    coll = db.apartments
    return coll

class HeadlessDriver():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def kill_driver(self):
        self.driver.close()
        self.driver.quit()

class RentalApartmentCrawler():
    def __init__(self):
        self.area = None
        self.no_of_rooms = 0
        self.max_rent = 0
        self.driver_instance = HeadlessDriver()
        self.commuting_calculator = TravelTimes()
        self.db = get_collection()

    def set_criteria(self, criteria):

        if 'area' in criteria:
            self.area = criteria.get('area')
        if 'no_of_rooms' in criteria:
            self.no_of_rooms = str(criteria.get('no_of_rooms'))
        if 'max_rent' in criteria:
            self.max_rent = str(criteria.get('max_rent'))

    def crawl_vuokraovi(self):
        driver = self.driver_instance.driver

        driver.get('https://www.vuokraovi.com')

        driver.find_element_by_xpath('//*[@id="inputLocationOrRentalUniqueNo"]').send_keys(self.area)
        #driver.find_element_by_xpath('//*[@id="roomCountButtons"]/div[' + self.no_of_rooms + ']/button').click()
        driver.find_element_by_xpath('//*[@id="rentalsMaxRent"]').send_keys(self.max_rent)
        driver.find_element_by_xpath('//*[@id="frontPageSearchPanelRentalsForm"]').submit()
        time.sleep(10)

        elements = driver.find_elements_by_xpath('//*[@class="list-item-container"]')
        found_posts = []
        for elem in elements:
            new_post = {}
            new_post['address'] = elem.find_element_by_class_name('address').text
            new_post['general_info'] = ', '.join([x.text for x in elem.find_elements_by_class_name('semi-bold')])
            new_post['rent'] = elem.find_element_by_class_name('rent').text
            new_post['free'] = elem.find_element_by_class_name('showing-lease-container').text
            new_post['link'] = elem.find_element_by_tag_name('a').get_attribute('href').split('?')[0]
            new_post['travel_times'] = self.commuting_calculator.get_travel_times(new_post['address'])
            found_posts.append(new_post)
            break
        self.driver_instance.kill_driver()

        self.db.insert_many(found_posts)
        
        for post in found_posts:
            del post['_id']
        return found_posts


def send_slack_notifications(found):
    webhook_url = 'SLACK_WEBHOOK_URL'

    for ad in found:
        text = 'Uusi asunto: {}. \nSijainti: {} \nVuokra: {}\n{}\n{}\n\n{}\n\n\n'.format(ad['general_info'], ad['address'], ad['rent'], ad['free'], ad['link'], ad['travel_times'])
        requests.post(
            webhook_url, data=json.dumps({'text':text}),
            headers={'Content-Type': 'application/json'}
        )

if __name__ == "__main__":
    crawler = RentalApartmentCrawler()
    crawler.set_criteria({
        'area': 'Helsinki',
        'no_of_rooms': [3],
        'max_rent': 1200
    })

    posts = crawler.crawl_vuokraovi()
    pp = pprint.PrettyPrinter(indent=2)
    for post in posts:
        pp.pprint(post)
