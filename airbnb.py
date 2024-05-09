import time
import random

from selenium import webdriver
import re
import logging

from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
                    self.logger.warning(f"Error extracting price from element:{url}")

                average = float(sum(price_list) / len(price_list)) if len(price_list) else 0
                return average

        except (NoSuchElementException, AttributeError) as e:
            self.logger.warning(f"something went wrong to fetch the content on {url}:{e}")
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

        except NoSuchElementException:
            print("No button on this page")
            return False

        except Exception as e:
            self.logger.error(f" next button click error:{e}")
            return False

    def get_holiday_country(self, url: str, country_name: str):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 10)
        try:
            # to close pub
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Fermer']")))
            button.click()
        except NoSuchElementException:
            print('Close button cookies not found')
        except TimeoutException:
            print("Close cookies button doesn't exist on page  ")

        country_input = self.driver.find_element(By.ID, "bigsearch-query-location-input")
        country_input.clear()
        country_input.send_keys(country_name)
        first_suggestion = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.smfh8a4")))

        # country_input.send_keys(Keys.ENTER)

        first_suggestion.click()

        return country_input.text

    def get_dates(self):
        pass

    def get_travelers_number(self):
        pass

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    url1 = "https://fr.airbnb.com/"
    scraper = AirbnbScraper()
    price1 = scraper.get_holiday_country(url1, "pari")
    print(price1)
    # scraper.close()
