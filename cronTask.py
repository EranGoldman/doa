from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from sys import argv
import sqlite3
import string
from random import *
import hashlib
import re
import base64
import requests


#TODO: Add unittest support
# import unittest
#
# class TestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.browser = webdriver.Firefox(executable_path='/opt/geckodriver')
#         self.addCleanup(self.browser.quit)
#
#     def testPageTitle(self):
#         self.browser.get('http://www.google.com')
#         self.assertIn('Google', self.browser.title)
#
# if __name__ == '__main__':
#     unittest.main(verbosity=2)
#

conn = sqlite3.connect('db/database.db')
mg_query = 'select * from mailgunCred;'
result = conn.execute(query)
mailgunurl = result[0][0]
mailgunapi = result[0][1]

driver = webdriver.Firefox(executable_path='/opt/geckodriver')
regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

query = "select * from domains;"
result = conn.execute(query)

for row in result:
    url = row[1]
    useremail = row[2]
    if re.match(regex, url):
        driver.get(url)
        driver.implicitly_wait(10)
        # element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "LiveOrNot"))
        # )
        try:
            element = driver.find_element_by_id('LiveOrNot')
            secret = element.get_attribute("data-secret")
            lenDiff = len(url) - len(driver.current_url)
            if (lenDiff == 1):
                url = url[:-1]
            elif(lenDiff == -1):
                url += '/'
            calc = (base64.b64encode(str.encode(url))).decode("utf-8").replace("=", "")
            if secret == calc:
                print(url, "is alive and tag in place")
            else:
                message = 'The tag for ' + url + 'is wrong\n'
                message += 'Tag : ' + secret + '\n'
                message += 'Should be : ' + calc + '\n'
                message += 'checked url : ' + driver.current_url
                files = {
                    'from': 'Dead or Alive <doa@gilgoldman.comE>',
                    'to': useremail,
                    'subject': '[DOA - ' + url + '] - Tag error',
                    'text': message
                }

                response = requests.post(mailgunurl, files=files, auth=('api', mailgunapi))
                print(url, "is alive and tag is wrong")
        except NoSuchElementException:
            print(url, "is accessable but DOL tag is missing")

    else:
        print(url, "is malformed")
    # print('element.get_attribute("data-secret")', element.get_attribute('data-secret'))

driver.quit()
