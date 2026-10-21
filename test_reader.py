
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

reader_url = os.getenv("QUIZ_DATABASE_URL")

if not reader_url:
    raise ValueError("QUIZ_DATABASE_URL is missing")

# Connect as the read-only quiz_reader
conn = psycopg2.connect(
    reader_url,
    connect_timeout=10
)

try:
    with conn.cursor() as cur:

        # Check current database role
        cur.execute("SELECT current_user;")
        print("Database role:", cur.fetchone()[0])

        # Read quiz questions
        cur.execute("""
            SELECT question_id, question_text, points
            FROM quiz_data.quiz_questions
            ORDER BY question_id;
        """)

        rows = cur.fetchall()

        print("Connection successful!")
        print("Total questions:", len(rows))

        for row in rows:
            print(row)

finally:
    conn.close()
