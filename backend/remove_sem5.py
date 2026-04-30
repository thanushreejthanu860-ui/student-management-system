import mysql.connector, os
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(host=os.getenv('DB_HOST','localhost'), user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''), database=os.getenv('DB_NAME','student_mgmt'))
cur = conn.cursor()

# Get sem 5 class IDs and subject IDs
cur.execute("SELECT id FROM classes WHERE semester=5")
class_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM subjects WHERE semester=5")
subject_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM students WHERE class_id IN ({})".format(','.join(map(str, class_ids))))
student_ids = [r[0] for r in cur.fetchall()]

if student_ids:
    ids = ','.join(map(str, student_ids))
    cur.execute(f"DELETE FROM activity_logs WHERE record_id IN ({ids}) AND table_affected='students'")
    cur.execute(f"DELETE FROM notifications WHERE student_id IN ({ids})")
    cur.execute(f"DELETE FROM attendance WHERE student_id IN ({ids})")
    cur.execute(f"DELETE FROM marks WHERE student_id IN ({ids})")
    cur.execute(f"DELETE FROM students WHERE id IN ({ids})")
    print(f"Deleted {len(student_ids)} students from sem 5")

if subject_ids:
    ids = ','.join(map(str, subject_ids))
    cur.execute(f"DELETE FROM faculty_assignments WHERE subject_id IN ({ids})")
    cur.execute(f"DELETE FROM subjects WHERE id IN ({ids})")
    print(f"Deleted {len(subject_ids)} subjects from sem 5")

if class_ids:
    ids = ','.join(map(str, class_ids))
    cur.execute(f"DELETE FROM faculty_assignments WHERE class_id IN ({ids})")
    cur.execute(f"DELETE FROM classes WHERE id IN ({ids})")
    print(f"Deleted {len(class_ids)} classes from sem 5")

conn.commit()
cur.close()
conn.close()
print("Done! Semester 5 removed.")
