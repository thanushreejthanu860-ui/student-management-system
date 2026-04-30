import mysql.connector
import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'student_mgmt')
)
cur = conn.cursor()

# Get all students
cur.execute("SELECT id, name FROM students")
students = cur.fetchall()

# Get all subjects
cur.execute("SELECT id FROM subjects WHERE semester = 5")
subject_ids = [row[0] for row in cur.fetchall()]

# Get admin id
cur.execute("SELECT id FROM users WHERE email = 'admin@college.com'")
admin_id = cur.fetchone()[0]

# Generate last 30 working days
def get_working_days(n=30):
    days = []
    d = date.today()
    while len(days) < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:  # Mon-Fri
            days.append(d)
    return days

working_days = get_working_days(30)

for student_id, name in students:
    for subject_id in subject_ids:
        for day in working_days:
            # 75-95% attendance probability
            status = 'present' if random.random() < 0.85 else 'absent'
            cur.execute("""
                INSERT IGNORE INTO attendance (student_id, subject_id, date, status, marked_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, subject_id, day, status, admin_id))
    conn.commit()
    print(f"Attendance added: {name}")

cur.close()
conn.close()
print("\nDone! Attendance updated for all students.")
