import mysql.connector
import os
import random
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'student_mgmt')
)
cur = conn.cursor()

# Add CS-B section
cur.execute("""
    INSERT IGNORE INTO classes (class_name, semester, department_id, academic_year)
    VALUES ('CS-B', 5, 1, '2024-25')
""")

# Add 6th subject
cur.execute("""
    INSERT IGNORE INTO subjects (subject_name, subject_code, credits, max_marks, pass_marks, department_id, semester)
    VALUES ('Artificial Intelligence', 'CS506', 4, 100, 40, 1, 5)
""")

conn.commit()

# Get class IDs
cur.execute("SELECT id FROM classes WHERE class_name = 'CS-A'")
class_a = cur.fetchone()[0]
cur.execute("SELECT id FROM classes WHERE class_name = 'CS-B'")
class_b = cur.fetchone()[0]

# Get all 6 subject IDs
cur.execute("SELECT id FROM subjects WHERE semester = 5 ORDER BY id")
subject_ids = [row[0] for row in cur.fetchall()]

# Get admin user id
cur.execute("SELECT id FROM users WHERE email = 'admin@college.com'")
admin_id = cur.fetchone()[0]

section_a = [
    ('Aarav Sharma',   '1CS21CS006', 'aarav@college.com',   '9876543215', 'Male'),
    ('Bhavya Patel',   '1CS21CS007', 'bhavya@college.com',  '9876543216', 'Female'),
    ('Chirag Mehta',   '1CS21CS008', 'chirag@college.com',  '9876543217', 'Male'),
    ('Divya Nair',     '1CS21CS009', 'divya@college.com',   '9876543218', 'Female'),
    ('Eshan Gupta',    '1CS21CS010', 'eshan@college.com',   '9876543219', 'Male'),
    ('Farida Khan',    '1CS21CS011', 'farida@college.com',  '9876543220', 'Female'),
    ('Gaurav Singh',   '1CS21CS012', 'gaurav@college.com',  '9876543221', 'Male'),
    ('Harini Reddy',   '1CS21CS013', 'harini@college.com',  '9876543222', 'Female'),
    ('Ishaan Verma',   '1CS21CS014', 'ishaan@college.com',  '9876543223', 'Male'),
    ('Jyoti Desai',    '1CS21CS015', 'jyoti@college.com',   '9876543224', 'Female'),
]

section_b = [
    ('Karan Malhotra', '1CS21CS016', 'karan@college.com',   '9876543225', 'Male'),
    ('Lavanya Iyer',   '1CS21CS017', 'lavanya@college.com', '9876543226', 'Female'),
    ('Manish Tiwari',  '1CS21CS018', 'manish@college.com',  '9876543227', 'Male'),
    ('Neha Joshi',     '1CS21CS019', 'neha@college.com',    '9876543228', 'Female'),
    ('Om Prakash',     '1CS21CS020', 'om@college.com',      '9876543229', 'Male'),
    ('Priya Pillai',   '1CS21CS021', 'priya@college.com',   '9876543230', 'Female'),
    ('Rahul Bose',     '1CS21CS022', 'rahul@college.com',   '9876543231', 'Male'),
    ('Sneha Kulkarni', '1CS21CS023', 'sneha@college.com',   '9876543232', 'Female'),
    ('Tarun Saxena',   '1CS21CS024', 'tarun@college.com',   '9876543233', 'Male'),
    ('Usha Menon',     '1CS21CS025', 'usha@college.com',    '9876543234', 'Female'),
]

def insert_students(students, class_id):
    for name, usn, email, phone, gender in students:
        cur.execute("""
            INSERT IGNORE INTO students (name, usn, email, phone, class_id, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, usn, email, phone, class_id, gender))
        conn.commit()

        cur.execute("SELECT id FROM students WHERE usn = %s", (usn,))
        student_id = cur.fetchone()[0]

        for subject_id in subject_ids:
            marks = random.randint(45, 98)
            cur.execute("""
                INSERT IGNORE INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by)
                VALUES (%s, %s, 'semester', %s, 100, %s)
            """, (student_id, subject_id, marks, admin_id))

        conn.commit()
        print(f"Added: {name} ({usn}) -> Class ID {class_id}")

insert_students(section_a, class_a)
insert_students(section_b, class_b)

cur.close()
conn.close()
print("\nDone! 20 students added across CS-A and CS-B with 6 subjects each.")
