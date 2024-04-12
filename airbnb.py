from selenium import webdriver
import re
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


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
            prices = self.driver.find_elements(By.CLASS_NAME, "_1jo4hgw")
            if prices:
                for price in prices:
                    last_price = price.find_element(By.CLASS_NAME, "_1y74zjx") or price.find_element(By.CLASS_NAME,
                                                                                                     "_1ks8cgb")
                    price_digit = re.sub(r'\D', '', last_price.text)
                    if price_digit.isdigit():
                        price_list.append(int(price_digit))
                average = sum(price_list) / len(price_list) if len(price_list) else 0
                return average

        except NoSuchElementException as e:
            self.logger.warning(f"something went wront to fetch the content from url:{e}")
            return 0

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    url = "https://fr.airbnb.com/s/Rio-de-Janeiro--Rio-de-Janeiro--Br%C3%A9sil/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-05-01&monthly_length=3&monthly_end_date=2024-08-01&price_filter_input_type=0&channel=EXPLORE&query=Rio%20de%20Janeiro%2C%20Br%C3%A9sil&date_picker_type=calendar&checkin=2024-04-28&checkout=2024-05-26&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=28&place_id=ChIJW6AIkVXemwARTtIvZ2xC3FA&search_mode=regular_search&adults=2"
    scraper = AirbnbScraper()
    price1 = scraper.get_average_price(url)
    print(price1)
    # scraper.close()
