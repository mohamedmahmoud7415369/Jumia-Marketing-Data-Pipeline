import duckdb
import pandas as pd
import os
from datetime import datetime

def generate_markdown_report(db_path='data/jumia_warehouse.duckdb', output_path='Docs/marketing_insights.md'):
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    # Ensure Docs directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    con = duckdb.connect(db_path)
    
    try:
        # Check for data
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]
        if 'fact_product_daily' not in table_names:
            print("Database is empty. Please run the Airflow pipeline first.")
            return
            
        # Start building Markdown content
        md_content = f"# 📊 Jumia Marketing Data Insights\n\n"
        md_content += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"
        
        # Table of Contents
        md_content += "## 📑 Table of Contents\n\n"
        md_content += "1. [Market Overview: Top Categories](#1-market-overview-top-categories)\n"
        md_content += "2. [Brand Performance: Top Rated Brands](#2-brand-performance-top-rated-brands)\n"
        md_content += "3. [Discount Opportunities](#3-discount-opportunities)\n"
        md_content += "4. [Price Distribution Analysis](#4-price-distribution-analysis)\n"
        md_content += "5. [Discount Effectiveness Analysis](#5-discount-effectiveness-analysis)\n"
        md_content += "6. [Brand Competitiveness Matrix](#6-brand-competitiveness-matrix)\n"
        md_content += "7. [Customer Satisfaction Leaders](#7-customer-satisfaction-leaders)\n"
        md_content += "8. [Review Velocity Indicators](#8-review-velocity-indicators)\n"
        md_content += "9. [Express Shipping Analysis](#9-express-shipping-analysis)\n"
        md_content += "10. [Official Store Performance](#10-official-store-performance)\n"
        md_content += "11. [Undervalued Products](#11-undervalued-products)\n"
        md_content += "12. [Premium Segment Analysis](#12-premium-segment-analysis)\n\n"
        md_content += "---\n\n"
        
        # 1. Market Overview
        md_content += "## 1. Market Overview: Top Categories\n"
        md_content += "**Insight:** Understanding which categories dominate the marketplace by product volume.\n\n"
        
        query_cat = """
        SELECT 
            p.category as Category, 
            COUNT(*) as "Product Count", 
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            ROUND(AVG(f.discount_pct), 2) as "Avg Discount %"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.category
        ORDER BY "Product Count" DESC
        LIMIT 10
        """
        df_cat = con.execute(query_cat).fetchdf()
        if not df_cat.empty:
            md_content += df_cat.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 2. Brand Performance
        md_content += "## 2. Brand Performance: Top Rated Brands\n"
        md_content += "**Insight:** Brands with established product portfolios (≥5 products), ranked by customer satisfaction.\n\n"
        
        query_brand = """
        SELECT 
            p.brand as Brand, 
            COUNT(*) as "Product Count", 
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            SUM(f.review_count) as "Total Reviews"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.brand
        HAVING COUNT(*) >= 5
        ORDER BY "Avg Rating" DESC, "Total Reviews" DESC
        LIMIT 10
        """
        df_brand = con.execute(query_brand).fetchdf()
        if not df_brand.empty:
            md_content += df_brand.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available or not enough products per brand.*\n\n"

        # 3. Discount Opportunities
        md_content += "## 3. Discount Opportunities\n"
        md_content += "**Insight:** High-quality products (Rating > 4.0) with minimal discounts (< 10%) - prime candidates for promotional campaigns.\n\n"
        
        query_opp = """
        SELECT 
            p.product_name as Product, 
            p.brand as Brand,
            p.category as Category,
            f.price_egp as "Price (EGP)", 
            f.rating as Rating, 
            f.review_count as Reviews,
            f.discount_pct as "Discount %"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.rating > 4.0 
          AND f.discount_pct < 10
          AND f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        ORDER BY f.rating DESC, f.review_count DESC
        LIMIT 15
        """
        df_opp = con.execute(query_opp).fetchdf()
        if not df_opp.empty:
            df_opp['Product'] = df_opp['Product'].str.slice(0, 45) + "..."
            md_content += df_opp.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No specific discount candidates found matching criteria.*\n\n"

        # 4. Price Distribution Analysis
        md_content += "## 4. Price Distribution Analysis\n"
        md_content += "**Insight:** Understanding price segmentation across the marketplace.\n\n"
        
        query_price = """
        SELECT 
            CASE 
                WHEN price_egp < 500 THEN '< 500 EGP (Budget)'
                WHEN price_egp < 1000 THEN '500-1000 EGP (Mid-Range)'
                WHEN price_egp < 2500 THEN '1000-2500 EGP (Premium)'
                WHEN price_egp < 5000 THEN '2500-5000 EGP (Luxury)'
                ELSE '> 5000 EGP (Ultra-Premium)'
            END as "Price Range",
            COUNT(*) as "Product Count",
            ROUND(AVG(rating), 2) as "Avg Rating",
            ROUND(AVG(discount_pct), 2) as "Avg Discount %"
        FROM fact_product_daily
        WHERE scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY 1
        ORDER BY MIN(price_egp)
        """
        df_price = con.execute(query_price).fetchdf()
        if not df_price.empty:
            md_content += df_price.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 5. Discount Effectiveness Analysis
        md_content += "## 5. Discount Effectiveness Analysis\n"
        md_content += "**Insight:** Correlation between discount levels and customer satisfaction scores.\n\n"
        
        query_discount = """
        SELECT 
            CASE 
                WHEN discount_pct = 0 THEN 'No Discount'
                WHEN discount_pct < 10 THEN '1-10%'
                WHEN discount_pct < 20 THEN '10-20%'
                WHEN discount_pct < 30 THEN '20-30%'
                WHEN discount_pct < 40 THEN '30-40%'
                ELSE '40%+'
            END as "Discount Range",
            COUNT(*) as "Product Count",
            ROUND(AVG(rating), 2) as "Avg Rating",
            ROUND(AVG(price_egp), 2) as "Avg Price (EGP)",
            SUM(review_count) as "Total Reviews"
        FROM fact_product_daily
        WHERE scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY 1
        ORDER BY MIN(discount_pct)
        """
        df_discount = con.execute(query_discount).fetchdf()
        if not df_discount.empty:
            md_content += df_discount.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 6. Brand Competitiveness Matrix
        md_content += "## 6. Brand Competitiveness Matrix\n"
        md_content += "**Insight:** Brands offering the best value proposition (high rating, competitive pricing).\n\n"
        
        query_competitive = """
        SELECT 
            p.brand as Brand,
            p.category as Category,
            COUNT(*) as Products,
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            ROUND(AVG(f.discount_pct), 2) as "Avg Discount %",
            ROUND(AVG(f.rating) / NULLIF(AVG(f.price_egp / 1000), 0), 2) as "Value Score"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.brand, p.category
        HAVING COUNT(*) >= 3 AND AVG(f.rating) > 3.5
        ORDER BY "Value Score" DESC
        LIMIT 15
        """
        df_competitive = con.execute(query_competitive).fetchdf()
        if not df_competitive.empty:
            md_content += df_competitive.to_markdown(index=False) + "\n\n"
            md_content += "> **Note:** Value Score = Avg Rating / (Avg Price in thousands). Higher is better.\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 7. Customer Satisfaction Leaders
        md_content += "## 7. Customer Satisfaction Leaders\n"
        md_content += "**Insight:** Products with exceptional ratings (≥ 4.5) and significant review volume (≥ 10 reviews).\n\n"
        
        query_satisfaction = """
        SELECT 
            p.product_name as Product,
            p.brand as Brand,
            p.category as Category,
            f.rating as Rating,
            f.review_count as Reviews,
            f.price_egp as "Price (EGP)"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.rating >= 4.5 
          AND f.review_count >= 10
          AND f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        ORDER BY f.rating DESC, f.review_count DESC
        LIMIT 15
        """
        df_satisfaction = con.execute(query_satisfaction).fetchdf()
        if not df_satisfaction.empty:
            df_satisfaction['Product'] = df_satisfaction['Product'].str.slice(0, 45) + "..."
            md_content += df_satisfaction.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No products found matching criteria.*\n\n"

        # 8. Review Velocity Indicators
        md_content += "## 8. Review Velocity Indicators\n"
        md_content += "**Insight:** Products ordered by review engagement. Products with 0 reviews are included as they may be new to the marketplace.\n\n"
        
        query_velocity = """
        SELECT 
            p.product_name as Product,
            p.brand as Brand,
            p.category as Category,
            f.review_count as "Total Reviews",
            f.rating as Rating,
            f.price_egp as "Price (EGP)"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
          AND f.review_count IS NOT NULL
        ORDER BY f.review_count DESC
        LIMIT 15
        """
        df_velocity = con.execute(query_velocity).fetchdf()
        if not df_velocity.empty:
            df_velocity['Product'] = df_velocity['Product'].str.slice(0, 45) + "..."
            md_content += df_velocity.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 9. Express Shipping Analysis
        md_content += "## 9. Express Shipping Analysis\n"
        md_content += "**Insight:** Performance comparison between Express and standard delivery products.\n\n"
        
        query_express = """
        SELECT 
            CASE WHEN p.is_express THEN 'Express Delivery' ELSE 'Standard Delivery' END as "Delivery Type",
            COUNT(*) as "Product Count",
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            SUM(f.review_count) as "Total Reviews",
            ROUND(AVG(f.discount_pct), 2) as "Avg Discount %"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.is_express
        ORDER BY p.is_express DESC
        """
        df_express = con.execute(query_express).fetchdf()
        if not df_express.empty:
            md_content += df_express.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 10. Official Store Performance
        md_content += "## 10. Official Store Performance\n"
        md_content += "**Insight:** Comparison between official brand stores and third-party sellers.\n\n"
        
        query_official = """
        SELECT 
            CASE WHEN p.is_official THEN 'Official Store' ELSE 'Third-Party Seller' END as "Store Type",
            COUNT(*) as "Product Count",
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            SUM(f.review_count) as "Total Reviews",
            ROUND(AVG(f.discount_pct), 2) as "Avg Discount %"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.is_official
        ORDER BY p.is_official DESC
        """
        df_official = con.execute(query_official).fetchdf()
        if not df_official.empty:
            md_content += df_official.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No data available.*\n\n"

        # 11. Undervalued Products (Hidden Gems)
        md_content += "## 11. Undervalued Products\n"
        md_content += "**Insight:** High-quality products with few reviews - potential hidden gems for marketing push.\n\n"
        
        query_hidden = """
        SELECT 
            p.product_name as Product,
            p.brand as Brand,
            p.category as Category,
            f.rating as Rating,
            f.review_count as Reviews,
            f.price_egp as "Price (EGP)",
            f.discount_pct as "Discount %"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.rating >= 4.0 
          AND f.review_count < 5
          AND f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        ORDER BY f.rating DESC, f.price_egp DESC
        LIMIT 15
        """
        df_hidden = con.execute(query_hidden).fetchdf()
        if not df_hidden.empty:
            df_hidden['Product'] = df_hidden['Product'].str.slice(0, 45) + "..."
            md_content += df_hidden.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No undervalued products found.*\n\n"

        # 12. Premium Segment Analysis
        md_content += "## 12. Premium Segment Analysis\n"
        md_content += "**Insight:** High-value products (> 2500 EGP) and their market performance.\n\n"
        
        query_premium = """
        SELECT 
            p.category as Category,
            p.brand as Brand,
            COUNT(*) as "Product Count",
            ROUND(AVG(f.price_egp), 2) as "Avg Price (EGP)",
            ROUND(AVG(f.rating), 2) as "Avg Rating",
            ROUND(AVG(f.discount_pct), 2) as "Avg Discount %",
            SUM(f.review_count) as "Total Reviews"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.price_egp > 2500
          AND f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        GROUP BY p.category, p.brand
        HAVING COUNT(*) >= 2
        ORDER BY "Avg Price (EGP)" DESC
        LIMIT 15
        """
        df_premium = con.execute(query_premium).fetchdf()
        if not df_premium.empty:
            md_content += df_premium.to_markdown(index=False) + "\n\n"
        else:
            md_content += "*No premium products found.*\n\n"

        # Summary Statistics
        md_content += "---\n\n"
        md_content += "## 📈 Summary Statistics\n\n"
        
        query_summary = """
        SELECT 
            COUNT(DISTINCT p.product_key) as "Total Products",
            COUNT(DISTINCT p.brand) as "Total Brands",
            COUNT(DISTINCT p.category) as "Total Categories",
            ROUND(AVG(f.price_egp), 2) as "Overall Avg Price (EGP)",
            ROUND(AVG(f.rating), 2) as "Overall Avg Rating",
            ROUND(AVG(f.discount_pct), 2) as "Overall Avg Discount %",
            SUM(f.review_count) as "Total Reviews"
        FROM fact_product_daily f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.scrape_timestamp = (SELECT MAX(scrape_timestamp) FROM fact_product_daily)
        """
        df_summary = con.execute(query_summary).fetchdf()
        if not df_summary.empty:
            md_content += df_summary.to_markdown(index=False) + "\n\n"

        md_content += "---\n\n"
        md_content += f"*Report generated automatically by Jumia Marketing Data Pipeline*\n"

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"Report successfully generated at: {output_path}")

    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
    finally:
        con.close()

if __name__ == "__main__":
    generate_markdown_report()
