#  Jumia Marketing Data Pipeline
<img width="1200" height="630" alt="image" src="https://github.com/user-attachments/assets/f978e982-321c-47f3-88bf-88652a6a4ddc" />

**Automated end-to-end data pipeline for Jumia Egypt marketplace analytics**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.5.0-green.svg)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Latest-yellow.svg)](https://duckdb.org/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This project implements a complete **data engineering pipeline** that:

1. **Scrapes** product data from Jumia Egypt using Selenium
2. **Processes** and transforms raw data into a dimensional model
3. **Stores** data in a DuckDB data warehouse (star schema)
4. **Generates** 12 comprehensive marketing insights
5. **Visualizes** analytics through an interactive Streamlit dashboard

Perfect for learning modern data engineering practices, e-commerce analytics, or building your portfolio!

---

## ✨ Features

### 🕷️ Web Scraping
- ✅ Automated Selenium-based scraping
- ✅ Multiple product categories support
- ✅ Anti-bot detection measures
- ✅ Runs in Docker with Selenium Grid

### 📊 Data Warehousing
- ✅ Dimensional modeling (star schema)
- ✅ DuckDB embedded database
- ✅ SCD Type 2 support for products
- ✅ Daily product snapshots

### 📈 Analytics & Insights
- ✅ 12 pre-built marketing insights
- ✅ Price distribution analysis
- ✅ Brand competitiveness metrics
- ✅ Customer satisfaction tracking
- ✅ Discount effectiveness analysis

### 🎨 Interactive Dashboard
- ✅ Real-time visualizations with Plotly
- ✅ KPI cards and summary statistics
- ✅ Responsive design
- ✅ Data refresh capabilities

### 🔄 Orchestration
- ✅ Apache Airflow DAG automation
- ✅ Scheduled daily runs
- ✅ Error handling and retries
- ✅ Task dependency management

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Jumia     │────▶│   Selenium   │────▶│  Raw CSV    │
│   Website   │     │   Scraper    │     │   Files     │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   DuckDB     │◀────│     ETL     │
                    │  Warehouse   │     │   Pipeline  │
                    └──────────────┘     └─────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        ┌───────────────┐     ┌──────────────┐
        │   Insights    │     │  Streamlit   │
        │   Reports     │     │  Dashboard   │
        └───────────────┘     └──────────────┘
```

**Technology Stack:**
- **Orchestration:** Apache Airflow
- **Scraping:** Selenium, BeautifulSoup
- **Database:** DuckDB
- **Processing:** Python, Pandas
- **Visualization:** Streamlit, Plotly
- **Infrastructure:** Docker, Docker Compose

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** version 1.29+
- **8GB RAM minimum** (12GB recommended)
- **10GB free disk space**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Jumia_Marketing_Data_Pipline.git
cd Jumia_Marketing_Data_Pipline

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be healthy (2-3 minutes)
docker-compose ps

# 4. Access Airflow UI
# URL: http://localhost:8080
# Username: admin
# Password: admin
```

### First Run

1. **Access Airflow UI:** http://localhost:8080
2. **Enable the DAG:** Toggle `jumia_marketing_pipeline` to ON
3. **Trigger manually:** Click "Trigger DAG" button
4. **Monitor progress:** Watch task execution in Graph/Tree view
5. **Check results:** View generated insights in `Docs/marketing_insights.md`

---

## 📁 Project Structure

```
Jumia_Marketing_Data_Pipline/
├── dags/
│   └── jumia_pipeline.py          # Airflow DAG definition
├── src/
│   ├── jumia_scraper.py           # Web scraping module
│   ├── create_schema.py           # Database schema
│   ├── etl_pipeline.py            # ETL processing
│   └── generate_insights.py       # Insights generation
├── dashboard/
│   ├── app.py                     # Streamlit dashboard
│   ├── config.py                  # Dashboard config
│   ├── utils.py                   # Dashboard utilities
│   └── README.md                  # Dashboard docs
├── data/
│   ├── raw/                       # Scraped CSV files
│   └── jumia_warehouse.duckdb     # DuckDB database
├── Docs/
│   ├── marketing_insights.md      # Generated insights
│   ├── TECHNICAL_DOCUMENTATION.md # Full tech docs
│   └── SCRAPER_DOCUMENTATION.md   # Scraper details
├── logs/                          # Airflow logs
├── docker-compose.yaml            # Service definitions
├── Dockerfile                     # Airflow image
├── requirements.txt               # Python dependencies
├── reset_project.ps1              # Reset script
└── README.md                      # This file
```

---

## 📖 Usage Guide

### Running the Pipeline

**Option 1: Airflow UI (Recommended)**
```bash
# 1. Access http://localhost:8080
# 2. Enable DAG toggle
# 3. Click "Trigger DAG"
```

**Option 2: Command Line**
```bash
# Trigger DAG manually
docker-compose exec airflow-scheduler airflow dags trigger jumia_marketing_pipeline

# Check DAG status
docker-compose exec airflow-scheduler airflow dags list
```

**Option 3: Scheduled Runs**
- DAG runs automatically daily at midnight
- Configure in `dags/jumia_pipeline.py`: `schedule_interval='@daily'`

### Running Individual Components

**Scraper Only:**
```bash
docker-compose exec airflow-webserver python /opt/airflow/src/jumia_scraper.py
```

**ETL Only:**
```bash
docker-compose exec airflow-webserver python /opt/airflow/src/etl_pipeline.py
```

**Insights Only:**
```bash
docker-compose exec airflow-webserver python /opt/airflow/src/generate_insights.py
```

### Running the Dashboard

```bash
# Method 1: Using Python directly (requires local installation)
pip install -r requirements.txt
python -m streamlit run dashboard/app.py

# Method 2: Inside Airflow container
docker-compose exec airflow-webserver streamlit run /opt/airflow/dashboard/app.py --server.port 8501

# Access dashboard at: http://localhost:8501
```

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | admin / admin |
| Selenium Grid | http://localhost:4444 | N/A |
| Selenium VNC | http://localhost:7900 | secret |
| Dashboard | http://localhost:8501 | N/A |

---

## 📚 Documentation

### Available Documentation

1. **[TECHNICAL_DOCUMENTATION.md](Docs/TECHNICAL_DOCUMENTATION.md)**
   - Complete architecture overview
   - Line-by-line code explanations
   - Infrastructure details
   - Database schema

2. **[SCRAPER_DOCUMENTATION.md](Docs/SCRAPER_DOCUMENTATION.md)**
   - Web scraping implementation
   - Selenium configuration
   - Error handling patterns
   - Performance optimization

4. **[TASKS.md](TASKS.md)**
   - Project roadmap
   - Feature backlog
   - Known issues

---

## 🔧 Configuration

### Modify Search Terms

Edit `src/jumia_scraper.py`:
```python
search_terms = [
    'Mobile Phones',
    'Tablets',
    'Electrical Appliances',
    'Computing',
    # Add your categories here
]
```

### Change Scraping Pages

Edit `src/jumia_scraper.py`:
```python
jumia_data = scrape_jumia_egypt(search_terms, pages_per_term=10)  # Change 10 to desired number
```

### Adjust DAG Schedule

Edit `dags/jumia_pipeline.py`:
```python
dag = DAG(
    'jumia_marketing_pipeline',
    schedule_interval='@daily',  # Options: @hourly, @weekly, '0 */6 * * *' (cron)
    ...
)
```

---

### Complete Reset

```bash
# WARNING: Deletes all data
docker-compose down -v
rm -rf data/
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Sample Insights Generated

The pipeline automatically generates 12 marketing insights:

1. **Market Overview** - Top categories by volume
2. **Brand Performance** - Top-rated brands
3. **Discount Opportunities** - High-quality, low-discount products
4. **Price Distribution** - Segmentation analysis
5. **Discount Effectiveness** - Correlation analysis
6. **Brand Competitiveness** - Value proposition metrics
7. **Customer Satisfaction** - Top-rated products
8. **Review Velocity** - Engagement indicators
9. **Express Shipping** - Delivery analysis
10. **Official Store Performance** - Store comparison
11. **Undervalued Products** - Hidden gems
12. **Premium Segment** - Luxury market analysis

---

## 🎓 Learning Objectives

This project demonstrates:

- ✅ **Data Pipeline Design** - End-to-end architecture
- ✅ **Web Scraping** - Selenium automation
- ✅ **ETL Development** - Data transformation
- ✅ **Data Modeling** - Dimensional modeling (star schema)
- ✅ **Workflow Orchestration** - Airflow DAGs
- ✅ **Data Visualization** - Streamlit dashboards
- ✅ **Containerization** - Docker & Docker Compose
- ✅ **Error Handling** - Production-ready patterns
- ✅ **Documentation** - Technical writing

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional product categories
- More sophisticated brand extraction
- Time-series analysis features
- Advanced visualizations
- Performance optimizations
- Unit tests

---

## 📝 License

This project is for educational purposes. Please respect Jumia's terms of service and robots.txt when scraping.

---

## 👨‍💻 Author

**Mohamed Mahmoud**  
ITI - Information Technology Institute  
**Supervised BY**
Dr. Eman Rasslan - EDA Course
---

## 🙏 Acknowledgments

- Apache Airflow community
- Selenium WebDriver team
- DuckDB developers
- Streamlit creators
---

**Last Updated:** 2025-11-26  
**Version:** 1.0.0

**Happy Data Engineering! 🚀**
