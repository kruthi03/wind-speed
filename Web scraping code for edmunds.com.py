from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the Edmunds used car page
url = "https://www.edmunds.com/used-all/"
driver.get(url)

wait = WebDriverWait(driver, 10)  # Explicit wait

# Ensure all elements are loaded before scraping
time.sleep(5)  # Increase wait if needed

# Scroll to load more cars (if the website uses lazy-loading)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Initialize lists to store data
car_names, prices, miles_driven, car_histories, variants, locations, below_market_prices, images, links = [], [], [], [], [], [], [], [], []

# Function to scrape car details from the current page
def scrape_cars():
    cars = driver.find_elements(By.XPATH, '//*[@id="results-container"]/ul/li')
    print(f"Found {len(cars)} cars on this page.")

    for index, car in enumerate(cars, start=1):
        try:
            car_name = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/div[1]/div[1]/h2/a/div[1]').text
        except:
            car_name = "N/A"

        try:
            price = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/span').text
        except:
            price = "N/A"

        try:
            miles = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/ul[1]/li[1]').text
        except:
            miles = "N/A"

        try:
            car_history = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/ul[1]/li[2]').text
        except:
            car_history = "N/A"

        try:
            variant = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/ul[1]/li[3]').text
        except:
            variant = "N/A"

        try:
            location = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/ul[1]/li[4]').text
        except:
            location = "N/A"

        try:
            below_market_price = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/div').text
        except:
            below_market_price = "N/A"

        try:
            image_element = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div/a/figure/img')
            image = image_element.get_attribute("src")
        except:
            image = "N/A"

        try:
            link = car.find_element(By.XPATH, f'//*[@id="results-container"]/ul/li[{index}]/div/div[2]/div/div[1]/div[1]/h2/a').get_attribute("href")
        except:
            link = "N/A"

        # Append data to lists
        car_names.append(car_name)
        prices.append(price)
        miles_driven.append(miles)
        car_histories.append(car_history)
        variants.append(variant)
        locations.append(location)
        below_market_prices.append(below_market_price)
        images.append(image)
        links.append(link)

# Scrape the first page
scrape_cars()

# Loop to click "Next" and scrape until we collect 1,000 rows
while len(car_names) < 1000:
    try:
        # Find the "Next" button
        next_button = driver.find_element(By.XPATH, "//*[@id='results-container']/div[2]/div[1]/nav/ul/li[8]/a")
        
        # Check if the next button is enabled
        if not next_button.is_enabled():
            print("No more pages available.")
            break

        # Click the "Next" button
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)  # Allow time for the next page to load

        # Scrape the new page
        scrape_cars()

    except Exception as e:
        print("No more pages or an error occurred:", e)
        break

# Close the browser
driver.quit()

# Create DataFrame
df = pd.DataFrame({
    "Car Name": car_names[:1000],  # Limit to 1000 rows
    "Price": prices[:1000],
    "Miles Driven": miles_driven[:1000],
    "Car History": car_histories[:1000],
    "Variant": variants[:1000],
    "Location": locations[:1000],
    "Below Market Price": below_market_prices[:1000],
    "Image URL": images[:1000],
    "Car Link": links[:1000]
})

# Display the data
print(df)

# Save to CSV
df.to_csv("edmunds_used_cars.csv", index=False)

print("Scraping completed! Data saved as 'edmunds_used_cars.csv'.")
