# Web Scraper CLI

This Web Scraper CLI is a versatile tool designed to scrape various types of data from websites. It supports scraping images, videos, sensitive data, and audio using a combination of libraries and techniques, including BeautifulSoup, Selenium, and asynchronous requests.

## Features

- **Image Scraping**: Extract image URLs from web pages.
- **Video Scraping**: Extract video source URLs.
- **Sensitive Data Scraping**: Extract specific text data based on XPath or CSS selectors.
- **Audio Scraping**: Extract audio source URLs.
- **JavaScript Handling**: Use Selenium to scrape JavaScript-heavy pages.
- **Asynchronous API Requests**: Fetch data from APIs asynchronously.
- **Proxy and User-Agent Rotation**: Use proxies and rotate user agents for requests.
- **Data Storage**: Store extracted data in a SQLite database.

## Requirements

- Python 3.x
- Required Python libraries:
  - `requests`
  - `lxml`
  - `beautifulsoup4`
  - `selenium`
  - `webdriver-manager`
  - `fake-useragent`
  - `aiohttp`
  - `retrying`
  - `python-dotenv`
  - `sqlite3` (comes with Python standard library)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/web-scraper-cli.git
   cd web-scraper-cli
   ```

2. **Install the Required Libraries**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the Web Scraper CLI, run the script and follow the prompts:

```bash
python scraper.py
```

### Steps

1. **Select Data Type**: Choose the type of data you want to scrape:
   - `1` for Images
   - `2` for Videos
   - `3` for Sensitive Data
   - `4` for Audio

2. **Enter URL**: Provide the URL of the website you want to scrape.

3. **Configuration**: The tool will load the appropriate configuration based on your choices and perform the scraping task.

## Configuration

The tool uses a `master_config.json` file to manage configurations for different scraping tasks. Ensure this file is correctly set up with the necessary details for each type of scraping.

## Important Notes

- **Rate Limiting**: Excessive use may result in temporary bans from websites. Use responsibly and consider adding delays between requests.
- **Disclaimer**: This tool is intended for educational and research purposes only. The author is not responsible for any misuse or damage caused by this tool.
