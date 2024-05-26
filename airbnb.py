import logging
import random
import re
import time
from datetime import datetime


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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

    def get_next_page_button(self, url: str):
        self.driver.get(url)
        page_number = 1
        url_list = []
        try:
            while True:
                print(f'we are {page_number}')
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".c1ytbx3a"))
                )

                if next_button.get_attribute("aria-disabled") == "true":
                    print("it's the last page")
                    break
                page_number += 1
                next_button.click()
                url_list.append(self.driver.current_url)
                time.sleep(random.uniform(3, 7))
            return url_list
        except NoSuchElementException:
            print("No button on this page")
            return False

        except Exception as e:
            self.logger.error(f" next button click error:{e}")
            return False

    def navigate_to_month(self, url: str, country_name: str, begin_day: datetime, end_day: datetime):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 10)

        # try to close the pub button if exist
        try:
            # to close pub
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Fermer']")))
            button.click()
        except NoSuchElementException:
            print('Close button cookies not found')
        except TimeoutException:
            print("Close cookies button doesn't exist on page  ")

        # Enter the name of the city where you are going
        country_input = wait.until(EC.element_to_be_clickable((By.ID, "bigsearch-query-location-input")))
        country_input.clear()
        country_input.send_keys(country_name)

        # click on the first suggestion
        first_suggestion = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.smfh8a4")))
        first_suggestion.click()

        # select the input month
        try:
            # month = self.driver.find_element(By.CLASS_NAME, "lk4ruxu")
            # month.click()
            month_flexible = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="search-tabpanel"]/div/div[3]/div[1]/div/div/div[2]')))
            month_flexible.click()
        except TimeoutException as e:
            raise e

        # select the interval of vacation date
        while True:
            try:
                next_month_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                           '[aria-label="Avancez pour passer au mois suivant."]')))
                try:
                    begin_day_selector = f'[data-testid="calendar-day-{begin_day.strftime("%d/%m/%Y")}"]'

                    begin_day_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, begin_day_selector)))
                    if begin_day_element:
                        begin_day_element.click()
                        while True:
                            try:
                                end_day_selector = f'[data-testid="calendar-day-{end_day.strftime("%d/%m/%Y")}"]'
                                end_day_element = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, end_day_selector)))
                                if end_day_element:
                                    end_day_element.click()
                                    break
                            except:
                                next_month_button.click()
                        break
                except:
                    next_month_button.click()
                    print('we are going to pass to the next month')

            except ElementNotInteractableException as er:
                print(f'error to interactable :{er}')
                raise er
            except Exception as e:
                print(f'Something went wrong: {e}')
                raise e
        # add the number of travellers
        travelers = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                           '[data-testid="structured-search-input-field-guests-button"]')))
        travelers.click()
        adults = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                        '[data-testid="stepper-adults-increase-button"]')))
        adults.click()
        adults.click()

        childs = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                        '[data-testid="stepper-children-increase-button"]')))
        childs.click()

        # click on the search button
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                               '[data-testid="structured-search-input-search-button"]')))
        search_button.click()

        return self.driver.current_url

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    url1 = "https://fr.airbnb.com/"
    scraper = AirbnbScraper()
    begin_vacation_day = datetime(2024, 6, 28)
    end_vacation_day = datetime(2024, 7, 12)
    country_date = scraper.navigate_to_month(url1, 'rio', begin_day=begin_vacation_day, end_day=end_vacation_day)
    all_pages = scraper.get_next_page_button(country_date)
    prices = []
    for page in all_pages:
        price1 = scraper.get_average_price(page)
        prices.append(price1)
    print(sum(prices)/len(prices))

    scraper.close()
