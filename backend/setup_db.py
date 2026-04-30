import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', '')
)
conn.autocommit = True
cur = conn.cursor()

db_name = os.getenv('DB_NAME', 'student_mgmt')
cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
cur.execute(f"USE `{db_name}`")

with open('schema_mysql.sql', 'r') as f:
    sql = f.read()

for statement in sql.split(';'):
    s = statement.strip()
    if s:
        try:
            cur.execute(s)
            print(f"OK: {s[:60]}...")
        except Exception as e:
            print(f"ERROR: {e}")

cur.close()
conn.close()
print("\nDatabase setup complete!")
