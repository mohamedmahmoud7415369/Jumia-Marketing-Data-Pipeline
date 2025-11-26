# Web Scraper Module - Detailed Code Documentation

## jumia_scraper.py - Complete Line-by-Line Analysis

**File Location:** `src/jumia_scraper.py`  
**Purpose:** Automated web scraping of Jumia Egypt marketplace using Selenium WebDriver  
**Lines of Code:** 203  
**Dependencies:** Selenium, BeautifulSoup4, pandas

---

## Table of Contents
1. [Imports and Dependencies](#imports-and-dependencies)
2. [Driver Setup Function](#driver-setup-function)
3. [Page Scraping Function](#page-scraping-function)
4. [Multi-Page Scraper Function](#multi-page-scraper-function)
5. [Main Execution](#main-execution)

---

## Imports and Dependencies

### Lines 1-10: Import Statements

```python
from bs4 import BeautifulSoup
```
- **Package:** BeautifulSoup4
- **Purpose:** HTML parsing library
- **Used For:** Extracting product data from page HTML
- **Why BeautifulSoup:** Easier to work with than raw HTML, handles malformed HTML gracefully

```python
from selenium import webdriver
```
- **Package:** Selenium WebDriver
- **Purpose:** Browser automation
- **Used For:** Loading JavaScript-heavy pages, handling dynamic content
- **Why Selenium:** Jumia uses JavaScript to render products; static scrapers (requests) won't work

```python
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
```
- **Service:** Manages ChromeDriver executable
- **Options:** Configures browser behavior (headless mode, user agent, etc.)
- **Purpose:** Customizes Chrome browser for scraping

```python
from webdriver_manager.chrome import ChromeDriverManager
```
- **Purpose:** Automatically downloads and manages ChromeDriver binary
- **Benefit:** No manual driver installation needed
- **Note:** Only used for local development; Docker uses remote Selenium

```python
import pandas as pd
```
- **Purpose:** Data manipulation and DataFrame creation
- **Used For:** Converting scraped list of dictionaries to DataFrame for CSV export

```python
import os
import time
from datetime import datetime
import random
```
- **os:** File system operations (directory creation, environment variables)
- **time:** Delays between requests (prevents getting blocked)
- **datetime:** Timestamping scraped data
- **random:** Random delays to mimic human behavior

---

## Driver Setup Function

### Lines 12-33: setup_driver()

```python
def setup_driver():
    """Setup Chrome Driver with options."""
```
**Function Purpose:**
- Creates and configures Selenium WebDriver instance
- Handles both local and remote (Docker) environments
- Returns ready-to-use driver object

```python
    options = Options()
```
- **Creates Options object:** Container for browser configuration
- **Effect:** Allows customization before driver initialization

```python
    # options.add_argument('--headless')  # Run in headless mode for automation
```
- **COMMENTED OUT:** Would run browser without GUI
- **Why Commented:** Helpful for debugging to see browser actions
- **Production Use:** Should be enabled for automated pipelines

```python
    options.add_argument('--disable-gpu')
```
- **Purpose:** Disables GPU hardware acceleration
- **Why:** Prevents crashes in Docker/headless environments
- **Effect:** More stable but slightly slower rendering

```python
    options.add_argument('--no-sandbox')
```
- **Purpose:** Disables Chrome's sandboxing feature
- **Why:** Required for running Chrome in Docker containers
- **Security Note:** Only use in controlled environments

```python
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
```
- **Purpose:** Sets browser user agent string
- **Why:** Makes scraper look like real Chrome browser
- **Effect:** Reduces chance of being blocked by anti-scraping measures
- **Format:** Standard Chrome on Windows 10 user agent

```python
    remote_url = os.environ.get('SELENIUM_REMOTE_URL')
```
- **Function:** Gets environment variable value
- **Variable:** SELENIUM_REMOTE_URL
- **Value in Docker:** http://selenium:4444/wd/hub
- **Value Locally:** None (not set)
- **Effect:** Determines local vs remote execution mode

```python
    if remote_url:
        print(f"Connecting to Remote Selenium Grid at {remote_url}")
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )
```
- **Condition:** If SELENIUM_REMOTE_URL exists (Docker environment)
- **webdriver.Remote:** Connects to remote Selenium Grid
- **command_executor:** URL of Selenium hub
- **Effect:** Uses containerized Chrome browser

```python
    else:
        print("Using Local Chrome Driver")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```
- **Condition:** If SELENIUM_REMOTE_URL not set (local development)
- **ChromeDriverManager().install():** Downloads correct ChromeDriver version
- **Service:** Starts local ChromeDriver process
- **Effect:** Uses locally installed Chrome

```python
    return driver
```
- **Returns:** Configured WebDriver instance ready for use

---

## Page Scraping Function

### Lines 35-151: scrape_jumia_product_page()

```python
def scrape_jumia_product_page(driver, url, search_term):
    """Scrape a single Jumia product page using Selenium"""
```
**Function Purpose:**
- Scrapes one page of search results
- Extracts all product cards on the page
- Returns list of product dictionaries

**Parameters:**
- `driver`: Selenium WebDriver instance
- `url`: Full URL to scrape
- `search_term`: Category being searched (for data labeling)

```python
    print(f"  Scraping URL: {url}")
```
- **Logging:** Prints current URL being scraped
- **Purpose:** Helps track progress and debug issues

```python
    try:
        driver.get(url)
```
- **driver.get():** Navigates browser to URL
- **Behavior:** 
  - Sends HTTP GET request
  - Waits for page load (JavaScript execution)
  - Renders full page with dynamic content
- **Effect:** Loads Jumia search results page

```python
        time.sleep(random.uniform(3, 5))  # Random delay
```
- **random.uniform(3, 5):** Random float between 3-5 seconds
- **Purpose:** Mimics human behavior
- **Why Variable:** Makes scraper less detectable
- **Effect:** Waits for page to fully render + appear human

```python
        soup = BeautifulSoup(driver.page_source, 'html.parser')
```
- **driver.page_source:** Gets fully-rendered HTML (after JavaScript)
- **'html.parser':** Built-in Python HTML parser
- **Effect:** Creates parseable HTML tree structure

```python
        products = []
```
- **Initialization:** Empty list to store product data
- **Purpose:** Accumulates products from this page

```python
        product_cards = soup.find_all('article', class_='prd')
```
- **find_all():** Finds all matching elements
- **'article':** HTML5 semantic tag
- **class_='prd':** Jumia's CSS classname for product cards
- **Result:** List of BeautifulSoup Tag objects (one per product)
- **Note:** This selector came from inspecting Jumia's HTML structure

```python
        if not product_cards:
            print("  No products found on this page.")
            return []
```
- **Validation:** Checks if any products were found
- **Why Important:** Page might be empty, selector might be wrong, or blocking occurred
- **Effect:** Returns empty list if no products

```python
        print(f"  Found {len(product_cards)} products.")
```
- **Logging:** Reports number of products found
- **Typical:** 20-40 products per page

```python
        for card in product_cards:
            try:
```
- **Loop:** Iterates through each product card
- **try-except:** Individual error handling per product
- **Why:** One bad product shouldn't break entire scrape

```python
                # Initialize variables
                name = 'N/A'
                brand = 'Unknown'
                price = 'N/A'
                old_price = None
                discount = None
                rating = 'No rating'
                reviews = 0
                img_url = 'N/A'
                product_url = 'N/A'
                is_official = False
                is_express = False
```
- **Default Values:** Safely handle missing data
- **Why:** Not all products have all fields (e.g., new products have no reviews)
- **Effect:** Ensures all required keys exist in output dictionary

```python
                # Name & Brand
                name_tag = card.find('h3', class_='name')
```
- **Selector:** `<h3 class="name">` (product name heading)
- **Method:** .find() returns first match (or None)
- **Purpose:** Extract product name

```python
                if name_tag:
                    name = name_tag.text.strip()
```
- **Validation:** Only process if tag exists
- **.text:** Gets text content of tag
- **.strip():** Removes leading/trailing whitespace
- **Example:** "  Samsung Galaxy S21  " → "Samsung Galaxy S21"

```python
                    if name:
                        brand = name.split()[0]  # Simple brand extraction
```
- **Logic:** Assumes first word is brand name
- **.split():** Splits on whitespace into list
- **[0]:** Takes first element
- **Example:** "Samsung Galaxy S21" → "Samsung"
- **Limitation:** Won't work for multi-word brands (e.g., "Xiaomi Redmi")

```python
                # Price
                price_tag = card.find('div', class_='prc')
                if price_tag:
                    price = price_tag.text.strip()
```
- **Selector:** `<div class="prc">` (price container)
- **Expected Format:** "1,250 EGP" or "250 EGP"
- **Extracttion:** Gets raw price text (cleaned later in ETL)

```python
                # Old Price
                old_price_tag = card.find('div', class_='old')
                if old_price_tag:
                    old_price = old_price_tag.text.strip()
```
- **Selector:** `<div class="old">` (crossed-out original price)
- **Purpose:** Captures pre-discount price
- **Note:** Only exists if product is on sale

```python
                # Discount
                discount_tag = card.find('div', class_='bdg _dsct')
                if discount_tag:
                    discount = discount_tag.text.strip()
```
- **Selector:** `<div class="bdg _dsct">` (discount badge)
- **Expected Format:** "-25%" or "50% OFF"
- **Purpose:** Captures discount percentage

```python
                # Rating & Reviews
                rev_tag = card.find('div', class_='rev')
```
- **Selector:** `<div class="rev">` (review container)
- **Contains:** Both rating and review count

```python
                if rev_tag:
                    stars_tag = rev_tag.find('div', class_='stars')
                    if stars_tag:
                        rating = stars_tag.text.strip().split(' ')[0]
```
- **Nested Find:** Looks for stars div within reviews div
- **Expected Format:** "4.5 out of 5"
- **.split(' ')[0]:** Extracts just the number (4.5)

```python
                    rev_text = rev_tag.get_text()
                    if '(' in rev_text and ')' in rev_text:
                        try:
                            reviews = int(rev_text.split('(')[1].split(')')[0])
                        except:
                            reviews = 0
```
- **Review Count Extraction:**
  - **Expected Format:** "4.5 out of 5 (123)"
  - **Logic:** Extracts number between parentheses
  - **.split('(')[1]:** Gets everything after '('
  - **.split(')')[0]:** Gets everything before ')'
  - **Result:** "123" → int(123)
- **Error Handling:** Sets to 0 if parsing fails

```python
                # Image
                img_tag = card.find('img', class_='img')
                if img_tag:
                    img_url = img_tag.get('data-src') or img_tag.get('src')
```
- **Lazy Loading:** Jumia uses `data-src` for lazy-loaded images
- **Fallback:** Uses `src` if `data-src` doesn't exist
- **or operator:** Returns first truthy value

```python
                # Link
                link_tag = card.find('a', class_='core')
                if link_tag:
                    href = link_tag.get('href')
                    if href:
                        product_url = f"https://www.jumia.com.eg{href}" if not href.startswith('http') else href
```
- **Selector:** `<a class="core">` (main product link)
- **.get('href'):** Gets href attribute value
- **URL Construction:**
  - **Relative URLs:** Prepends "https://www.jumia.com.eg"
  - **Absolute URLs:** Uses as-is
  - **Example:** "/product-123" → "https://www.jumia.com.eg/product-123"

```python
                # Express Shipping
                if card.find('svg', class_='xprss') or card.find('div', class_='_xs'):
                    is_express = True
```
- **Multiple Selectors:** Checks for either SVG icon or div badge
- **Purpose:** Detects if product offers express delivery
- **Default:** False (set in initialization)

```python
                # Official Store
                if card.find('div', class_='bdg _mall'):
                    is_official = True
```
- **Selector:** `<div class="bdg _mall">` (official store badge)
- **Purpose:** Identifies products from official brand stores
- **Marketing Value:** Official stores typically have higher trust

```python
                product_data = {
                    'search_term': search_term,
                    'product_name': name,
                    'brand': brand,
                    'price_egp': price,
                    'old_price': old_price,
                    'discount': discount,
                    'rating': rating,
                    'review_count': reviews,
                    'is_express': is_express,
                    'is_official': is_official,
                    'scrape_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'product_url': product_url,
                    'image_url': img_url
                }
```
- **Dictionary Creation:** Organizes all extracted data
- **Keys:** Match database schema column names
- **scrape_timestamp:** Exact time of data collection
- **Format:** "2025-11-26 15:30:45"

```python
                products.append(product_data)
```
- **Accumulation:** Adds product to list
- **Effect:** Builds up list of all products on page

```python
            except Exception as e:
                print(f"Error parsing product card: {e}")
                continue
```
- **Error Handling:** Catches any parsing errors for individual product
- **Logging:** Prints error message
- **continue:** Skips to next product (doesn't crash entire scrape)

```python
        return products
```
- **Returns:** List of product dictionaries (0-40 products typically)

```python
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        return []
```
- **Page-Level Error Handling:** Catches complete page failures
- **Returns:** Empty list if entire page scrape fails

---

## Multi-Page Scraper Function

### Lines 153-176: scrape_jumia_egypt()

```python
def scrape_jumia_egypt(search_terms, pages_per_term=3):
    """Scrape multiple pages for multiple search terms from Jumia Egypt using Selenium"""
```
**Function Purpose:**
- Orchestrates scraping across multiple categories and pages
- Manages driver lifecycle
- Aggregates all results

**Parameters:**
- `search_terms`: List of categories to search
- `pages_per_term`: Number of pages per category (default: 3)

```python
    driver = setup_driver()
    all_products = []
```
- **Driver Creation:** Sets up browser once (reused across all pages)
- **Accumulator:** Will store all products from all searches

```python
    try:
        for search_term in search_terms:
            print(f"Scraping Jumia for: {search_term}")
```
- **Category Loop:** Iterates through each search term
- **Logging:** Reports current category being scraped

```python
            for page in range(1, pages_per_term + 1):
```
- **Page Loop:** Scrapes multiple pages per category
- **range(1, pages_per_term + 1):** 
  - pages_per_term=3 → range(1, 4) → [1, 2, 3]
  - Jumia pages in format: `page=1`, `page=2`, etc.

```python
                # URL construction
                base_url = f"https://www.jumia.com.eg/catalog/?q={search_term.replace(' ', '+')}"
```
- **Base URL:** Jumia search endpoint
- **.replace(' ', '+'):** URL-encodes spaces
  - Example: "Mobile Phones" → "Mobile+Phones"
- **Query Parameter:** `?q=` triggers search

```python
                separator = '&' if '?' in base_url else '?'
```
- **Logic:** Determines correct separator for additional parameters
- **If '?' exists:** Use '&' for next parameter
- **If '?' missing:** Use '?' to start parameters
- **Smart URL Building:** Handles varying URL formats

```python
                url = f"{base_url}{separator}page={page}"
```
- **Complete URL:** Adds page number
- **Examples:**
  - Page 1: ".../catalog/?q=Mobile+Phones&page=1"
  - Page 2: ".../catalog/?q=Mobile+Phones&page=2"

```python
                # Scrape the page
                products = scrape_jumia_product_page(driver, url, search_term)
                all_products.extend(products)
```
- **Scraping:** Calls single-page scraper function
- **.extend():** Adds all products to master list (vs .append which adds list as single element)

```python
    finally:
        driver.quit()
```
- **Cleanup:** Always closes browser, even if error occurs
- **Why finally:** Ensures driver closes to free resources
- **driver.quit():** Terminates browser process completely

```python
    return pd.DataFrame(all_products)
```
- **DataFrame Conversion:** Converts list of dictionaries to pandas DataFrame
- **Columns:** Automatically from dictionary keys
- **Rows:** One per product
- **Effect:** Ready for CSV export or further processing

---

## Main Execution

### Lines 177-203: Script Entry Point

```python
search_terms = [
    'Mobile Phones',
    'Tablets',
    'Electrical Appliances',
    'Computing'
]
```
- **Hard-coded Categories:** Default search terms
- **Egyptian Market:** Selected based on Jumia Egypt's popular categories
- **Customizable:** Can be modified based on business needs

```python
if __name__ == "__main__":
```
- **Guard Clause:** Only runs if file executed directly (not imported)
- **Purpose:** Allows module to be imported without auto-running

```python
    print("Starting Jumia Egypt scraping...")
```
- **Start Message:** User feedback

```python
    # Run the scraper
    jumia_data = scrape_jumia_egypt(search_terms, pages_per_term=10)
```
- **Execution:** Runs full scrape
- **pages_per_term=10:** 10 pages per category
- **Total Pages:** 4 categories × 10 pages = 40 pages
- **Expected Products:** ~800-1600 products (20-40 per page)

```python
    print(f"Scraped {len(jumia_data)} products from Jumia")
```
- **Summary:** Reports total products scraped

```python
    # Save raw data
    output_dir = r"d:\ITI-Data_Engineer\EDA_Dr.Eman\Jumia_Marketing_Data_Pipline\data\raw"
    os.makedirs(output_dir, exist_ok=True)
```
- **Raw String:** `r""` prevents backslash interpretation
- **Absolute Path:** Full Windows path to output directory
- **os.makedirs:** Creates directory if doesn't exist
- **exist_ok=True:** No error if directory already exists

```python
    filename = f"jumia_raw_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
```
- **Timestamp Format:** YYYYMMDD_HHMMSS
- **Example:** "jumia_raw_data_20251126_153045.csv"
- **Purpose:** Unique filename for each scrape run

```python
    output_path = os.path.join(output_dir, filename)
```
- **Path Joining:** Combines directory and filename
- **Cross-Platform:** Works on Windows/Linux/Mac

```python
    jumia_data.to_csv(output_path, index=False)
```
- **CSV Export:** Saves DataFrame to CSV file
- **index=False:** Don't include row numbers in CSV
- **Effect:** Creates raw data file for ETL pipeline

```python
    print(f"Raw data saved to {output_path}")
    print(jumia_data.head())
```
- **Confirmation:** Shows save location
- **.head():** Displays first 5 rows as preview

---

## Key Design Patterns

### 1. **Graceful Degradation**
- Default values for all fields
- Individual product error handling
- Page-level error handling
- Returns partial results even if some pages fail

### 2. **Anti-Bot Measures**
- Random delays (3-5 seconds)
- Realistic user agent
- Human-like browsing patterns

### 3. **Production-Ready Error Handling**
- Try-except at multiple levels
- Informative error logging
- Continues on errors (doesn't crash)

### 4. **Flexible Deployment**
- Environment variable detection (local vs Docker)
- Automatic driver management
- Configurable search terms and pages

### 5. **Data Quality**
- Timestamps all data
- Preserves raw values (cleaning in ETL)
- Captures metadata (search term, scrape time)

---

## Performance Characteristics

**Speed:**
- ~5 seconds per page (including delay)
- ~40 pages = ~3-4 minutes total
- Can be parallelized with multiple drivers

**Resource Usage:**
- **Memory:** ~200-300 MB per Chrome instance
- **Network:** ~1-2 MB per page
- **CPU:** Moderate (HTML parsing)

**Scalability:**
- Linear with number of pages
- Can run 3-4 concurrent drivers safely
- Limited by Selenium Grid capacity in Docker

---

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| No products found | Selector changed | Inspect page, update selectors |
| Timeout errors | Slow network | Increase wait times |
| ChromeDriver version mismatch | Chrome updated | Use WebDriverManager |
| Blocked by Jumia | Too fast scraping | Increase random delays |
| Memory leaks | Driver not closed | Ensure .quit() in finally block |

---

**Document Version:** 1.0  
**Module:** jumia_scraper.py  
**Total Lines:** 203  
**Last Updated:** 2025-11-26
