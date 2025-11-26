from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add src to path so we can import our modules
sys.path.append('/opt/airflow/src')

# Import our functions
# Note: These imports might fail locally if dependencies aren't installed in the local env,
# but they will work inside the Airflow Docker container.
try:
    from jumia_scraper import scrape_jumia_egypt, search_terms
    from etl_pipeline import run_etl
    from create_schema import create_schema
except ImportError:
    print("Could not import modules. This is expected if running outside the Docker container.")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_scraper_task():
    """Wrapper to run the scraper."""
    # Ensure output dir exists
    os.makedirs('/opt/airflow/data/raw', exist_ok=True)
    
    print("Starting Scraper Task...")
    scrape_jumia_egypt(search_terms, pages_per_term=5) # Reduced pages for daily run
    print("Scraper Task Complete.")

def run_etl_task():
    """Wrapper to run the ETL."""
    # Ensure schema exists first
    create_schema(db_path='/opt/airflow/data/jumia_warehouse.duckdb')
    
    # Run ETL
    # We need to patch the paths in etl_pipeline.py or ensure it uses relative paths correctly
    # For now, we assume etl_pipeline uses 'data/raw' which maps correctly in Docker
    run_etl()

with DAG(
    'jumia_marketing_pipeline',
    default_args=default_args,
    description='Daily Jumia Scraping and ETL Pipeline',
    schedule_interval='@weekly',
    start_date=datetime(2025, 11, 23),
    catchup=False,
    tags=['jumia', 'marketing'],
) as dag:

    t1 = PythonOperator(
        task_id='scrape_jumia_data',
        python_callable=run_scraper_task,
    )

    t2 = PythonOperator(
        task_id='process_and_load_data',
        python_callable=run_etl_task,
    )

    t1 >> t2
