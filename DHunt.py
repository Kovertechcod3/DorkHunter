import requests
from lxml import html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import logging
import os
from itertools import cycle
from selenium.common.exceptions import TimeoutException
import json
import asyncio
import aiohttp
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from retrying import retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define configuration templates for different scraping tasks
CONFIG_TEMPLATES = {
    "image": {
        "API_URL": "https://api.example.com/image-data",
        "PROXY_LIST": [
            "http://your_proxy1:port",
            "http://your_proxy2:port",
            "http://your_proxy3:port"
        ],
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        "XPATH": "//img/@src",
        "CSS_SELECTOR": "img",
        "DB_NAME": "image_data.db"
    },
    "video": {
        "API_URL": "https://api.example.com/video-data",
        "PROXY_LIST": [
            "http://your_proxy1:port",
            "http://your_proxy2:port",
            "http://your_proxy3:port"
        ],
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        "XPATH": "//video/source/@src",
        "CSS_SELECTOR": "video source",
        "DB_NAME": "video_data.db"
    },
    "sensitive": {
        "API_URL": "https://api.example.com/sensitive-data",
        "PROXY_LIST": [
            "http://your_proxy1:port",
            "http://your_proxy2:port",
            "http://your_proxy3:port"
        ],
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        "XPATH": "//div[@class='sensitive-info']/text()",
        "CSS_SELECTOR": ".sensitive-info",
        "DB_NAME": "sensitive_data.db"
    },
    "audio": {
        "API_URL": "https://api.example.com/audio-data",
        "PROXY_LIST": [
            "http://your_proxy1:port",
            "http://your_proxy2:port",
            "http://your_proxy3:port"
        ],
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
        "XPATH": "//audio/source/@src",
        "CSS_SELECTOR": "audio source",
        "DB_NAME": "audio_data.db"
    }
}

def load_config(scraping_type, url):
    """Load configuration based on the scraping type and URL."""
    if scraping_type not in CONFIG_TEMPLATES:
        raise ValueError("Invalid scraping type.")
    
    config = CONFIG_TEMPLATES[scraping_type].copy()
    config['SCRAPING_URL'] = url
    return config

# Function to extract image paths using BeautifulSoup
def fetch_image_paths(url):
    """Fetch image paths from a given URL."""
    logging.info(f"Fetching image paths from {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')

        image_paths = [img['src'] for img in images if 'src' in img.attrs]
        logging.info(f"Found {len(image_paths)} images.")
        return image_paths
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return []

# Function to extract data using XPath and CSS Selectors
@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def extract_data_with_xpath_and_css(url):
    """Extract data using XPath and CSS selectors."""
    logging.info(f"Starting data extraction from {url} using XPath and CSS selectors.")
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        xpath_elements = tree.xpath('//div[@class="example-class"]/text()')
        logging.debug(f"Extracted {len(xpath_elements)} elements using XPath.")

        soup = BeautifulSoup(response.content, 'html.parser')
        css_elements = soup.select('.example-class')
        logging.debug(f"Extracted {len(css_elements)} elements using CSS selectors.")

        return xpath_elements, css_elements
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return [], []

# Function to handle JavaScript-heavy pages using Selenium
def extract_data_with_selenium(url):
    """Extract data from JavaScript-heavy pages using Selenium."""
    logging.info(f"Starting data extraction from {url} using Selenium.")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.example-class')))
        content = driver.page_source

        soup = BeautifulSoup(content, 'html.parser')
        elements = soup.select('.example-class')
        logging.debug(f"Extracted {len(elements)} elements using Selenium.")

        return elements
    except TimeoutException as e:
        logging.error(f"Timeout while extracting data with Selenium from {url}: {e}")
        return []
    except Exception as e:
        logging.error(f"Error extracting data with Selenium from {url}: {e}")
        return []
    finally:
        driver.quit()

# Asynchronous function to fetch data from an API
async def fetch_data_from_api(api_url):
    """Fetch data from an API asynchronously."""
    logging.info(f"Fetching data from API: {api_url}")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                response.raise_for_status()
                data = await response.json()
                logging.debug(f"Fetched data from API: {data}")
                return data
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching data from API {api_url}: {e}")
            return {}

# Function to use proxies and rotate user agents
@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def fetch_data_with_proxies_and_user_agents(url, proxy_list):
    """Fetch data using proxies and rotate user agents."""
    logging.info(f"Fetching data from {url} using proxies and rotating user agents.")
    ua = UserAgent()
    proxy_pool = cycle(proxy_list)

    for _ in range(len(proxy_list)):
        proxy = next(proxy_pool)
        headers = {'User-Agent': ua.random}
        proxies = {'http': proxy, 'https': proxy}

        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()
            logging.debug(f"Successfully fetched data with proxy {proxy}.")
            return response.content
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error fetching data with proxy {proxy}: {e}")
            continue
    logging.error("All proxies failed.")
    return None

# Function to validate extracted data
def validate_data(data):
    """Validate extracted data."""
    # Implement specific validation logic as needed
    return all(data)

# Function to store data in a SQLite database
def store_data_in_db(data, db_name='scraped_data.db'):
    """Store extracted data in a SQLite database."""
    if not validate_data(data):
        logging.error("Data validation failed. Data not stored.")
        return

    logging.info(f"Storing data in database: {db_name}")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    ''')

    cursor.executemany('INSERT INTO data (content) VALUES (?)', [(str(item),) for item in data])
    conn.commit()
    conn.close()

# Main function
def main():
    print("Welcome to the Web Scraper CLI!")
    print("Please select the type of data you want to scrape:")
    print("1. Images")
    print("2. Videos")
    print("3. Sensitive Data")
    print("4. Audio")

    choice = input("Enter the number corresponding to your choice: ").strip()

    scraping_types = {
        "1": "image",
        "2": "video",
        "3": "sensitive",
        "4": "audio"
    }

    scraping_type = scraping_types.get(choice)

    if not scraping_type:
        print("Invalid choice. Please try again.")
        return

    url = input("Please enter the URL you want to scrape: ").strip()

    try:
        config = load_config(scraping_type, url)
        logging.info(f"Configuration loaded for {scraping_type} scraping.")
        logging.info(f"Scraping URL: {config['SCRAPING_URL']}")

        proxy_list = config.get('PROXY_LIST', [])

        with ThreadPoolExecutor(max_workers=5) as executor:
            xpath_data, css_data = executor.submit(extract_data_with_xpath_and_css, url).result()
            logging.info("Data extracted using XPath: %s", xpath_data)
            logging.info("Data extracted using CSS Selectors: %s", css_data)

            selenium_data = executor.submit(extract_data_with_selenium, url).result()
            logging.info("Data extracted using Selenium: %s", selenium_data)

            image_paths = executor.submit(fetch_image_paths, url).result()
            logging.info("Image paths extracted: %s", image_paths)

        asyncio.run(fetch_data_from_api(config['API_URL']))

        proxy_data = fetch_data_with_proxies_and_user_agents(url, proxy_list)
        logging.info("Data fetched with proxies and user agents: %s", proxy_data)

        store_data_in_db(xpath_data + css_data + selenium_data + image_paths, config['DB_NAME'])

    except ValueError as e:
        logging.error(e)

if __name__ == "__main__":
    main()
