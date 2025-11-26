import pandas as pd
import duckdb
import os
from datetime import datetime
import glob

DB_PATH = 'data/jumia_warehouse.duckdb'
RAW_DATA_DIR = 'data/raw'

def clean_price(price_str):
    """Clean price string to float."""
    if pd.isna(price_str) or price_str == 'N/A':
        return None
    # Remove 'EGP', commas, and whitespace
    clean = str(price_str).replace('EGP', '').replace(',', '').strip()
    try:
        return float(clean)
    except ValueError:
        return None

def clean_rating(rating_str):
    """Clean rating string to float."""
    if pd.isna(rating_str) or rating_str == 'No rating':
        return None
    try:
        return float(str(rating_str).split()[0])
    except (ValueError, IndexError):
        return None

def run_etl():
    """Main ETL function."""
    print("Starting ETL Process...")
    
    # 1. Extract: Load all CSVs from raw directory
    all_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
    if not all_files:
        print("No raw data found.")
        return

    df_list = []
    for filename in all_files:
        try:
            # Check if file has content
            if os.path.getsize(filename) < 10:  # Skip files smaller than 10 bytes
                print(f"Skipping empty file: {filename}")
                continue
            df = pd.read_csv(filename)
            if not df.empty:
                df_list.append(df)
                print(f"Loaded {len(df)} records from {os.path.basename(filename)}")
            else:
                print(f"Skipping empty dataframe from: {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
    if not df_list:
        print("No valid data found in raw files.")
        return
    
    raw_df = pd.concat(df_list, ignore_index=True)
    print(f"Loaded {len(raw_df)} total raw records from {len(df_list)} files.")

    # 2. Transform
    # Clean numeric columns
    raw_df['price_egp'] = raw_df['price_egp'].apply(clean_price)
    raw_df['old_price'] = raw_df['old_price'].apply(clean_price)
    
    # Calculate discount percentage if missing
    mask_discount = raw_df['discount'].isna() & raw_df['old_price'].notna() & raw_df['price_egp'].notna()
    raw_df.loc[mask_discount, 'discount'] = ((raw_df['old_price'] - raw_df['price_egp']) / raw_df['old_price'] * 100).round(1).astype(str) + '%'
    
    # Clean discount to float for analysis
    raw_df['discount_pct'] = raw_df['discount'].str.replace('%', '').str.replace('-', '').astype(float)
    
    raw_df['rating'] = raw_df['rating'].apply(clean_rating)
    
    # Handle missing values
    raw_df['review_count'] = raw_df['review_count'].fillna(0).astype(int)
    raw_df['brand'] = raw_df['brand'].fillna('Unknown')
    raw_df['is_official'] = raw_df['is_official'].fillna(False)
    raw_df['is_express'] = raw_df['is_express'].fillna(False)
    
    # Date handling
    today = datetime.now().date()
    raw_df['scrape_date'] = pd.to_datetime(raw_df['scrape_timestamp']).dt.date

    # 3. Load to DuckDB
    con = duckdb.connect(DB_PATH)
    
    # --- Load Dim_Date (Simple generation for range) ---
    # In a real scenario, we'd generate a full calendar. Here we ensure today exists.
    # Check if date exists, if not insert
    # For simplicity in this demo, we'll just ensure the current date key exists
    date_key = int(today.strftime('%Y%m%d'))
    
    con.execute(f"""
    INSERT OR IGNORE INTO dim_date (date_key, full_date, year, month, day_of_month)
    VALUES ({date_key}, '{today}', {today.year}, {today.month}, {today.day})
    """)
    
    # --- Load Dim_Product (SCD Type 1 for simplicity first, then Type 2 logic) ---
    # For this iteration, we will do a "Merge/Upsert" logic.
    # If product_url exists, update attributes. If not, insert.
    
    # We need to assign surrogate keys.
    # Let's load raw data into a temp table first
    con.register('raw_stage', raw_df)
    
    # Insert new products into dim_product
    con.execute("""
    INSERT INTO dim_product (
        product_key, product_url, product_name, brand, category, 
        image_url, is_official, is_express, effective_date, is_current
    )
    SELECT 
        nextval('product_key_seq'), 
        product_url, 
        product_name, 
        brand, 
        search_term, 
        image_url, 
        is_official, 
        is_express, 
        CURRENT_DATE, 
        TRUE
    FROM raw_stage
    WHERE product_url NOT IN (SELECT product_url FROM dim_product)
    GROUP BY product_url, product_name, brand, search_term, image_url, is_official, is_express
    """)
    
    # --- Load Fact Table ---
    con.execute(f"""
    INSERT INTO fact_product_daily (
        fact_id, product_key, date_key, price_egp, old_price_egp, 
        discount_pct, rating, review_count, scrape_timestamp
    )
    SELECT 
        nextval('fact_id_seq'),
        dp.product_key,
        {date_key},
        rs.price_egp,
        rs.old_price,
        rs.discount_pct,
        rs.rating,
        rs.review_count,
        CAST(rs.scrape_timestamp AS TIMESTAMP)
    FROM raw_stage rs
    JOIN dim_product dp ON rs.product_url = dp.product_url
    """)
    
    print("ETL Completed Successfully.")
    
    # Verification count
    count = con.execute("SELECT COUNT(*) FROM fact_product_daily").fetchone()[0]
    print(f"Total rows in Fact Table: {count}")
    
    con.close()

if __name__ == "__main__":
    run_etl()
