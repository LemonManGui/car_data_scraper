from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome WebDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode for no browser UI
service = Service("/usr/lib/chromium-browser/chromedriver")  # Update path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = "https://www.carplus.es/coches-segunda-mano/"

def scrape_main_page(url):

    # 1) Accept cookies if button is present
    try:
        wait = WebDriverWait(driver, 10)
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.rgc-button.js-rgc-accept-all"))
        )
        cookie_button.click()
        # Brief pause after click
        time.sleep(1)
    except Exception as e:
        print("Cookie accept button not found or not clickable:", e)

    # 2) Wait for page content to load
    time.sleep(3)

    # Find all car listing links on the main page
    car_links = []
    cars = driver.find_elements(By.CLASS_NAME, 'vehicle-card-container')
    for car in cars:
        link = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
        if link:
            car_links.append(link)

    return car_links


def scrape_car_page(url):
    driver.get(url)
    time.sleep(1)  # Wait for the page to load

    car_details = {}

    # Title information
    title_group = driver.find_element(By.CLASS_NAME, 'title-group')
    car_details['Make'] = title_group.find_element(By.CLASS_NAME, 'title').text.strip()
    car_details['Variant'] = title_group.find_element(By.CLASS_NAME, 'subtitle').text.strip()

    # Features
    features = driver.find_elements(By.CSS_SELECTOR, 'div.vehicle-features p[data-v-ce991cf7=""]')
    car_details['Fuel_Type'] = features[0].text.strip()
    car_details['Year'] = features[1].text.strip()
    car_details['Kms'] = features[2].text.strip()
    car_details['Transmission'] = features[4].text.strip()
    car_details['Seats'] = features[5].text.strip()

    # Price
    price_group = driver.find_element(By.CLASS_NAME, 'price-group')
    car_details['Price'] = features[1].text.strip()

    # Colors and consumption
    specs = driver.find_elements(By.CLASS_NAME, 'specification--label')
    car_details['Exterior_colour'] = specs[5].text.strip()
    car_details['Interior_colour'] = specs[6].text.strip()
    car_details['Consumption'] = specs[3].text.strip()

    # Dealer and crawl info
    car_details['Dealer_name'] = "CarPlus"
    car_details['Dealer_website'] = url
    car_details['Date_of_crawl'] = datetime.now().strftime('%Y-%m-%d')

    return car_details


def click_next_page():
    """
    Clicks the 'Siguiente' button to move to the next page.
    If there's no next page or the button is not found, it will raise an exception.
    """
    time.sleep(2)
    next_button = driver.find_element(By.CSS_SELECTOR, "button.next-button")
    time.sleep(2)
    driver.execute_script("arguments[0].click();", next_button)
    time.sleep(2)  # Adjust sleep if needed


def main():
    car_data = []

    # Visit the initial page and scrape
    page = 1
    driver.get(BASE_URL)
    while True:
        print(f"Scraping page {page}...")
        car_links = scrape_main_page(BASE_URL)
        if not car_links:
            # No cars found; break out of loop
            break

        for link in car_links:
            try:
                car_details = scrape_car_page(link)
                car_data.append(car_details)
            except Exception as e:
                print(f"Error scraping {link}: {e}")

        # Try to go to the next page
        try:
            driver.get(BASE_URL)
            for i in range(page):
                click_next_page()
            page += 1
        except Exception as e:
            print("No more pages or error clicking next button.", e)
            break

    # Output the collected data
    for car in car_data:
        print(car)

    print(len(car_data))


if __name__ == "__main__":
    main()
    driver.quit()  # Quit the browser session after scraping
