from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

# Set up Chrome WebDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode for no browser UI
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
    #price_group.find_element(By.CLASS_NAME, 'previous-price').text.strip()

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

def get_current_page():
    # Locate the pagination label (e.g., "Pagina 2 - 19")
    pagination_label = driver.find_element(By.CLASS_NAME, "pagination--label")  # Update selector if necessary
    page_text = pagination_label.text  # Text will be something like "Pagina 2 - 19"
    current_page = int(page_text.split()[1])  # Extract the current page number (e.g., 2 from "Pagina 2")
    return current_page

def increment_page_number():
    # Get the current page number
    current_page = get_current_page()

    # Increment the page number by 1
    new_page = current_page + 1

    # Update the pagination HTML with the new page number
    pagination_label = driver.find_element(By.CLASS_NAME, "pagination--label")  # Locate the pagination element
    page_text = pagination_label.text

    # Replace the old page number with the incremented page number
    new_text = page_text.replace(f"Pagina {current_page}", f"Pagina {new_page}")

    # Update the text of the pagination label element
    driver.execute_script("arguments[0].textContent = arguments[1];", pagination_label, new_text)

def main():
    car_links = scrape_main_page(BASE_URL)
    car_data = []

    

    for link in car_links:
        if len(car_data) % 16 == 0 and len(car_data) != 0:
            increment_page_number()
        try:
            car_details = scrape_car_page(link)
            car_data.append(car_details)
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    # Output the collected data
    for car in car_data:
        print(car)

    print(len(car_data))

if __name__ == "__main__":
    main()
    driver.quit()  # Quit the browser session after scraping

