import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("ALTER TABLE moods ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")

conn.commit()
conn.close()
print("Column added.")
