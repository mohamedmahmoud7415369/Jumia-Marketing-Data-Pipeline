from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time
from datetime import datetime
import random

def setup_driver():
    """Setup Chrome Driver with options."""
    options = Options()
    # options.add_argument('--headless')  # Run in headless mode for automation
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Check if running in Docker (remote Selenium)
    remote_url = os.environ.get('SELENIUM_REMOTE_URL')
    
    if remote_url:
        print(f"Connecting to Remote Selenium Grid at {remote_url}")
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )
    else:
        print("Using Local Chrome Driver")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    return driver

def scrape_jumia_product_page(driver, url, search_term):
    """Scrape a single Jumia product page using Selenium"""
    print(f"  Scraping URL: {url}")
    try:
        driver.get(url)
        time.sleep(random.uniform(3, 5))  # Random delay
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        products = []
        # Robust selector from previous debugging
        product_cards = soup.find_all('article', class_='prd')
        
        if not product_cards:
            print("  No products found on this page.")
            return []
            
        print(f"  Found {len(product_cards)} products.")
        
        for card in product_cards:
            try:
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

                # Name & Brand
                name_tag = card.find('h3', class_='name')
                if name_tag:
                    name = name_tag.text.strip()
                    if name:
                        brand = name.split()[0] # Simple brand extraction

                # Price
                price_tag = card.find('div', class_='prc')
                if price_tag:
                    price = price_tag.text.strip()

                # Old Price
                old_price_tag = card.find('div', class_='old')
                if old_price_tag:
                    old_price = old_price_tag.text.strip()

                # Discount
                discount_tag = card.find('div', class_='bdg _dsct')
                if discount_tag:
                    discount = discount_tag.text.strip()

                # Rating & Reviews
                rev_tag = card.find('div', class_='rev')
                if rev_tag:
                    stars_tag = rev_tag.find('div', class_='stars')
                    if stars_tag:
                        rating = stars_tag.text.strip().split(' ')[0]
                    
                    rev_text = rev_tag.get_text()
                    if '(' in rev_text and ')' in rev_text:
                        try:
                            reviews = int(rev_text.split('(')[1].split(')')[0])
                        except:
                            reviews = 0

                # Image
                img_tag = card.find('img', class_='img')
                if img_tag:
                    img_url = img_tag.get('data-src') or img_tag.get('src')

                # Link
                link_tag = card.find('a', class_='core')
                if link_tag:
                    href = link_tag.get('href')
                    if href:
                        product_url = f"https://www.jumia.com.eg{href}" if not href.startswith('http') else href
                        
                # Express Shipping
                if card.find('svg', class_='xprss') or card.find('div', class_='_xs'):
                        is_express = True
                        
                # Official Store
                if card.find('div', class_='bdg _mall'):
                    is_official = True

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
                
                products.append(product_data)
                
            except Exception as e:
                print(f"Error parsing product card: {e}")
                continue
                
        return products
        
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        return []

def scrape_jumia_egypt(search_terms, pages_per_term=3):
    """Scrape multiple pages for multiple search terms from Jumia Egypt using Selenium"""
    driver = setup_driver()
    all_products = []
    
    try:
        for search_term in search_terms:
            print(f"Scraping Jumia for: {search_term}")
            
            for page in range(1, pages_per_term + 1):
                # URL construction
                base_url = f"https://www.jumia.com.eg/catalog/?q={search_term.replace(' ', '+')}"
                separator = '&' if '?' in base_url else '?'
                url = f"{base_url}{separator}page={page}"
                
                # Scrape the page
                products = scrape_jumia_product_page(driver, url, search_term)
                all_products.extend(products)
                
    finally:
        driver.quit()
    
    return pd.DataFrame(all_products)

# Define Egyptian market search terms
search_terms = [
    'Mobile Phones',
    'Tablets',
    'Electrical Appliances',
    'Computing'
]

if __name__ == "__main__":
    print("Starting Jumia Egypt scraping...")
    
    # Run the scraper
    jumia_data = scrape_jumia_egypt(search_terms, pages_per_term=10)
    
    print(f"Scraped {len(jumia_data)} products from Jumia")

    # Save raw data
    output_dir = r"d:\ITI-Data_Engineer\EDA_Dr.Eman\Jumia_Marketing_Data_Pipline\data\raw"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"jumia_raw_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = os.path.join(output_dir, filename)
    
    jumia_data.to_csv(output_path, index=False)
    print(f"Raw data saved to {output_path}")
    print(jumia_data.head())
