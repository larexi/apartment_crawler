import json
import pprint
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from travel_times import TravelTimes

GECKODRIVER = './geckodriver'

# def get_collection():
#     # client = MongoClient('localhost', 27017)
#     db = client.apartment_db
#     coll = db.apartments
#     return coll

class HeadlessDriver():
    def __init__(self):
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(executable_path='./geckodriver')

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

        driver.find_element(By.XPATH, '//*[@id="inputLocationOrRentalUniqueNo"]').send_keys(self.area)
        #driver.find_element_by_xpath('//*[@id="roomCountButtons"]/div[' + self.no_of_rooms + ']/button').click()
        driver.find_element(By.XPATH, '//*[@id="rentalsMaxRent"]').send_keys(self.max_rent)
        driver.find_element(By.XPATH, '//*[@id="frontPageSearchPanelRentalsForm"]').submit()
        time.sleep(10)

        elements = driver.find_elements(By.XPATH, '//*[@class="list-item-container"]')
        found_posts = []
        for elem in elements:
            new_post = {}
            new_post['address'] = elem.find_element(By.CLASS_NAME, 'address').text
            new_post['general_info'] = ', '.join([x.text for x in elem.find_elements(By.CLASS_NAME, 'semi-bold')])
            new_post['rent'] = elem.find_element(By.CLASS_NAME, 'rent').text
            new_post['free'] = elem.find_element(By.CLASS_NAME, 'showing-lease-container').text
            new_post['link'] = elem.find_element(By.TAG_NAME, 'a').get_attribute('href').split('?')[0]
            # new_post['travel_times'] = self.commuting_calculator.get_travel_times(new_post['address'])
            found_posts.append(new_post)
            break

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
