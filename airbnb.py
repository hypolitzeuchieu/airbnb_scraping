import time
import random

from selenium import webdriver
import re
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AirbnbScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_average_price(self, url: str) -> float:
        price_list = []
        self.driver.get(url)
        try:
            prices = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "_1jo4hgw"))
            )
            if prices:
                try:
                    for price in prices:
                        last_price = price.find_element(By.CLASS_NAME, "_1y74zjx") or price.find_element(By.CLASS_NAME,
                                                                                                         "_1ks8cgb")
                        price_digit = re.sub(r'\D', '', last_price.text)
                        if price_digit.isdigit():
                            price_list.append(float(price_digit))
                except (NoSuchElementException, AttributeError):
                    self.logger.warning(f"Error extracting price from element:{price}")

                average = float(sum(price_list) / len(price_list)) if len(price_list) else 0
                return average

        except (NoSuchElementException, AttributeError) as e:
            self.logger.warning(f"something went wront to fetch the content on {url}:{e}")
            return 0

    def get_next_page_button(self, url: str) -> bool:
        self.driver.get(url)
        page_number = 1
        try:
            while True:
                print(f"we are on page:{page_number}")
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".c1ytbx3a"))
                )

                if next_button.get_attribute("aria-disabled") == "true":
                    print("it's the last page")
                    break

                page_number += 1
                next_button.click()
                time.sleep(random.uniform(3, 7))

        except Exception as e:
            self.logger.error(f" next button click error:{e}")
            return False

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    url1 = "https://fr.airbnb.com/"
    scraper = AirbnbScraper()
    price1 = scraper.get_average_price(url1)
    print(price1)
    scraper.close()
