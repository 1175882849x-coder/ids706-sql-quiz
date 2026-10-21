
import os
import psycopg2
from dotenv import load_dotenv

# Step 1: Load environment variables
load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found in .env")

# Step 2: Connect to PostgreSQL
conn = psycopg2.connect(
    database_url,
    connect_timeout=10
)

try:
    # Step 3: Execute SQL query
    with conn.cursor() as cur:
        cur.execute("""
            SELECT product_id, product_name, price
            FROM quiz_data.products
            ORDER BY product_id;
        """)

        # Step 4: Fetch results
        rows = cur.fetchall()

        print("Connection successful!")

        for row in rows:
            print(row)

finally:
    conn.close()