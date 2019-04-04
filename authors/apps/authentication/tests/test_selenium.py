import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class TestSelenium(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(
            os.getenv('CHROME_WEBDRIVER'))

    def test_incorrect_github_credentials(self):
        driver = self.driver
        driver.get("http://localhost:8000/login/github/")
        self.assertIn("GitHub", driver.title)
        elem = driver.find_element_by_name("login")
        elem.send_keys("joseph.mutiga@gmail.com")
        elem = driver.find_element_by_name("password")
        elem.send_keys("jdaf")
        elem.send_keys(Keys.RETURN)
        self.assertIn("Incorrect username or password.", driver.page_source)

    def test_incorrect_facebook_credentials(self):
        driver = self.driver
        driver.get("http://localhost:8000/login/facebook/")
        self.assertIn("Facebook", driver.title)
        elem = driver.find_element_by_name("email")
        elem.send_keys("joseph.mutiga@gmail.com")
        elem = driver.find_element_by_name("pass")
        elem.send_keys("jdaf")
        elem.send_keys(Keys.RETURN)
        self.assertIn("The password that you've entered is incorrect.", 
                    driver.page_source)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
