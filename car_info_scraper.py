from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode for no browser UI
service = Service("/Users/gui/Desktop/chromedriver")  # Make sure to replace this with the path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = "https://www.carplus.es/coches-segunda-mano/"

def scrape_main_page(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

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
    time.sleep(3)  # Wait for the page to load
    
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
    car_details['Transmission'] = features[3].text.strip()
    car_details['Seats'] = features[4].text.strip()

    # Price
    price_group = driver.find_element(By.CLASS_NAME, 'price-group')
    car_details['Price'] = price_group.find_element(By.CLASS_NAME, 'previous-price').text.strip()

    # Colors and consumption
    specs = driver.find_elements(By.CLASS_NAME, 'specification--label')
    car_details['Exterior_colour'] = specs[0].text.strip()
    car_details['Interior_colour'] = specs[1].text.strip()
    car_details['Consumption'] = specs[2].text.strip()

    # Dealer and crawl info
    car_details['Dealer_name'] = "CarPlus"
    car_details['Dealer_website'] = url
    car_details['Date_of_crawl'] = datetime.now().strftime('%Y-%m-%d')

    return car_details

def main():
    main_url = BASE_URL + "/coche"
    car_links = scrape_main_page(main_url)
    car_data = []

    for link in car_links:
        try:
            car_details = scrape_car_page(link)
            car_data.append(car_details)
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    # Output the collected data
    for car in car_data:
        print(car)

if __name__ == "__main__":
    main()
    driver.quit()  # Quit the browser session after scraping
