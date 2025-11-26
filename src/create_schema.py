import duckdb
import os

def create_schema(db_path='data/jumia_warehouse.duckdb'):
    """Initialize the DuckDB schema for the Jumia Data Warehouse."""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    con = duckdb.connect(db_path)
    
    # 1. Dimension: Date
    con.execute("""
    CREATE TABLE IF NOT EXISTS dim_date (
        date_key INTEGER PRIMARY KEY,
        full_date DATE,
        day_name VARCHAR,
        day_of_week INTEGER,
        day_of_month INTEGER,
        month_name VARCHAR,
        month INTEGER,
        year INTEGER,
        is_weekend BOOLEAN
    );
    """)
    
    # 2. Dimension: Product (SCD Type 2 support fields included)
    con.execute("""
    CREATE TABLE IF NOT EXISTS dim_product (
        product_key INTEGER PRIMARY KEY, -- Surrogate Key
        product_url VARCHAR, -- Natural Key
        product_name VARCHAR,
        brand VARCHAR,
        category VARCHAR,
        image_url VARCHAR,
        is_official BOOLEAN,
        is_express BOOLEAN,
        effective_date DATE,
        expiration_date DATE,
        is_current BOOLEAN
    );
    """)
    
    # 3. Fact: Product Daily Snapshot
    con.execute("""
    CREATE TABLE IF NOT EXISTS fact_product_daily (
        fact_id INTEGER PRIMARY KEY, -- Optional surrogate for fact
        product_key INTEGER,
        date_key INTEGER,
        price_egp DOUBLE,
        old_price_egp DOUBLE,
        discount_pct DOUBLE,
        rating DOUBLE,
        review_count INTEGER,
        scrape_timestamp TIMESTAMP,
        FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
        FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
    );
    """)
    
    # Sequence for keys if needed (DuckDB supports sequences)
    con.execute("CREATE SEQUENCE IF NOT EXISTS product_key_seq START 1;")
    con.execute("CREATE SEQUENCE IF NOT EXISTS fact_id_seq START 1;")

    print(f"Schema initialized in {db_path}")
    con.close()

if __name__ == "__main__":
    create_schema()
