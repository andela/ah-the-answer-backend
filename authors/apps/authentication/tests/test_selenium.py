import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from django.urls import reverse



class TestSelenium(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(
            os.getenv('CHROME_WEBDRIVER'))
        self.current_site = os.getenv('AH_HOST')
        self.github_url = self.current_site + "login/github/"
        self.facebook_url = self.current_site + "login/facebook/"

    def test_incorrect_github_credentials(self):
        driver = self.driver
        driver.get(self.github_url)
        self.assertIn("GitHub", driver.title)
        elem = driver.find_element_by_name("login")
        elem.send_keys("joseph.mutiga@gmail.com")
        elem = driver.find_element_by_name("password")
        elem.send_keys("jdaf")
        elem.send_keys(Keys.RETURN)
        self.assertIn("Incorrect username or password.", driver.page_source)

    def test_incorrect_facebook_credentials(self):
        driver = self.driver
        driver.get(self.facebook_url)
        self.assertIn("Facebook", driver.title)
        elem = driver.find_element_by_name("email")
        elem.send_keys("joseph.mutiga@gmail.com")
        elem = driver.find_element_by_name("pass")
        elem.send_keys("jdaf")
        elem.send_keys(Keys.RETURN)
        self.assertIn("The password you’ve entered is incorrect.",
                      driver.page_source)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
