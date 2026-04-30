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

# ── Sections: 7 sections across sem 2, 4, 6 ──
# Sem 2: CS-A, CS-B, CS-C
# Sem 4: CS-D, CS-E
# Sem 6: CS-F, CS-G

sections = [
    ('CS-A', 2, '2024-25'),
    ('CS-B', 2, '2024-25'),
    ('CS-C', 2, '2024-25'),
    ('CS-D', 4, '2024-25'),
    ('CS-E', 4, '2024-25'),
    ('CS-F', 6, '2024-25'),
    ('CS-G', 6, '2024-25'),
]

for name, sem, year in sections:
    cur.execute("""
        INSERT IGNORE INTO classes (class_name, semester, department_id, academic_year)
        VALUES (%s, %s, 1, %s)
    """, (name, sem, year))
conn.commit()
print("Sections created.")

# ── Subjects per semester ──
subjects = [
    # Sem 2
    ('Mathematics II',        'CS201', 4, 100, 40, 1, 2),
    ('Digital Electronics',   'CS202', 4, 100, 40, 1, 2),
    ('Data Structures',       'CS203', 4, 100, 40, 1, 2),
    ('OOP with Java',         'CS204', 4, 100, 40, 1, 2),
    ('Computer Organization', 'CS205', 4, 100, 40, 1, 2),
    ('Communication Skills',  'CS206', 2, 100, 40, 1, 2),
    # Sem 4
    ('Design & Analysis of Algorithms', 'CS401', 4, 100, 40, 1, 4),
    ('Operating Systems',               'CS402', 4, 100, 40, 1, 4),
    ('Database Management Systems',     'CS403', 4, 100, 40, 1, 4),
    ('Computer Networks',               'CS404', 4, 100, 40, 1, 4),
    ('Theory of Computation',           'CS405', 4, 100, 40, 1, 4),
    ('Microprocessors',                 'CS406', 4, 100, 40, 1, 4),
    # Sem 6
    ('Compiler Design',        'CS601', 4, 100, 40, 1, 6),
    ('Machine Learning',       'CS602', 4, 100, 40, 1, 6),
    ('Cloud Computing',        'CS603', 4, 100, 40, 1, 6),
    ('Information Security',   'CS604', 4, 100, 40, 1, 6),
    ('Software Engineering',   'CS605', 4, 100, 40, 1, 6),
    ('Big Data Analytics',     'CS606', 4, 100, 40, 1, 6),
]

for s in subjects:
    cur.execute("""
        INSERT IGNORE INTO subjects (subject_name, subject_code, credits, max_marks, pass_marks, department_id, semester)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, s)
conn.commit()
print("Subjects created.")

# ── Get class IDs ──
cur.execute("SELECT id, class_name, semester FROM classes ORDER BY semester, class_name")
classes = {(r[1], r[2]): r[0] for r in cur.fetchall()}

# ── Get subject IDs per semester ──
cur.execute("SELECT id, semester FROM subjects")
subjects_by_sem = {}
for sid, sem in cur.fetchall():
    subjects_by_sem.setdefault(sem, []).append(sid)

# ── Admin ID ──
cur.execute("SELECT id FROM users WHERE email='admin@college.com'")
admin_id = cur.fetchone()[0]

# ── Students: 7 sections × ~9-10 students = ~63 students ──
all_students = {
    ('CS-A', 2): [
        ('Aditya Kumar',    '2CS22CS001', 'aditya@college.com',   '9800000001', 'Male'),
        ('Ananya Singh',    '2CS22CS002', 'ananya@college.com',   '9800000002', 'Female'),
        ('Arjun Mehta',     '2CS22CS003', 'arjun@college.com',    '9800000003', 'Male'),
        ('Avni Sharma',     '2CS22CS004', 'avni@college.com',     '9800000004', 'Female'),
        ('Bharat Patel',    '2CS22CS005', 'bharat@college.com',   '9800000005', 'Male'),
        ('Chitra Nair',     '2CS22CS006', 'chitra@college.com',   '9800000006', 'Female'),
        ('Deepak Verma',    '2CS22CS007', 'deepak@college.com',   '9800000007', 'Male'),
        ('Diya Reddy',      '2CS22CS008', 'diya@college.com',     '9800000008', 'Female'),
        ('Farhan Khan',     '2CS22CS009', 'farhan@college.com',   '9800000009', 'Male'),
    ],
    ('CS-B', 2): [
        ('Geeta Iyer',      '2CS22CS010', 'geeta@college.com',    '9800000010', 'Female'),
        ('Harsh Gupta',     '2CS22CS011', 'harsh@college.com',    '9800000011', 'Male'),
        ('Isha Desai',      '2CS22CS012', 'isha@college.com',     '9800000012', 'Female'),
        ('Jay Malhotra',    '2CS22CS013', 'jay@college.com',      '9800000013', 'Male'),
        ('Kavya Pillai',    '2CS22CS014', 'kavya@college.com',    '9800000014', 'Female'),
        ('Lokesh Tiwari',   '2CS22CS015', 'lokesh@college.com',   '9800000015', 'Male'),
        ('Meera Joshi',     '2CS22CS016', 'meera@college.com',    '9800000016', 'Female'),
        ('Nikhil Bose',     '2CS22CS017', 'nikhil@college.com',   '9800000017', 'Male'),
        ('Ojasvi Saxena',   '2CS22CS018', 'ojasvi@college.com',   '9800000018', 'Female'),
    ],
    ('CS-C', 2): [
        ('Pranav Menon',    '2CS22CS019', 'pranav@college.com',   '9800000019', 'Male'),
        ('Preethi Rao',     '2CS22CS020', 'preethi@college.com',  '9800000020', 'Female'),
        ('Rahul Das',       '2CS22CS021', 'rahuldas@college.com', '9800000021', 'Male'),
        ('Riya Kulkarni',   '2CS22CS022', 'riya@college.com',     '9800000022', 'Female'),
        ('Rohan Sinha',     '2CS22CS023', 'rohan@college.com',    '9800000023', 'Male'),
        ('Sakshi Pandey',   '2CS22CS024', 'sakshi@college.com',   '9800000024', 'Female'),
        ('Siddharth Roy',   '2CS22CS025', 'siddharth@college.com','9800000025', 'Male'),
        ('Simran Kaur',     '2CS22CS026', 'simran@college.com',   '9800000026', 'Female'),
        ('Tanmay Shah',     '2CS22CS027', 'tanmay@college.com',   '9800000027', 'Male'),
    ],
    ('CS-D', 4): [
        ('Akash Mishra',    '4CS22CS001', 'akash@college.com',    '9800000028', 'Male'),
        ('Amrita Ghosh',    '4CS22CS002', 'amrita@college.com',   '9800000029', 'Female'),
        ('Aniket Patil',    '4CS22CS003', 'aniket@college.com',   '9800000030', 'Male'),
        ('Aparna Nambiar',  '4CS22CS004', 'aparna@college.com',   '9800000031', 'Female'),
        ('Aryan Chopra',    '4CS22CS005', 'aryan@college.com',    '9800000032', 'Male'),
        ('Deeksha Hegde',   '4CS22CS006', 'deeksha@college.com',  '9800000033', 'Female'),
        ('Dhruv Agarwal',   '4CS22CS007', 'dhruv@college.com',    '9800000034', 'Male'),
        ('Divyanka Rao',    '4CS22CS008', 'divyanka@college.com', '9800000035', 'Female'),
        ('Gaurav Nair',     '4CS22CS009', 'gauravnair@college.com','9800000036', 'Male'),
    ],
    ('CS-E', 4): [
        ('Harsha Reddy',    '4CS22CS010', 'harsha@college.com',   '9800000037', 'Female'),
        ('Ishan Trivedi',   '4CS22CS011', 'ishan@college.com',    '9800000038', 'Male'),
        ('Jhanvi Mehta',    '4CS22CS012', 'jhanvi@college.com',   '9800000039', 'Female'),
        ('Karthik Menon',   '4CS22CS013', 'karthik@college.com',  '9800000040', 'Male'),
        ('Keerthi Pillai',  '4CS22CS014', 'keerthi@college.com',  '9800000041', 'Female'),
        ('Kunal Sharma',    '4CS22CS015', 'kunal@college.com',    '9800000042', 'Male'),
        ('Lakshmi Iyer',    '4CS22CS016', 'lakshmi@college.com',  '9800000043', 'Female'),
        ('Madhav Singh',    '4CS22CS017', 'madhav@college.com',   '9800000044', 'Male'),
        ('Manasa Rao',      '4CS22CS018', 'manasa@college.com',   '9800000045', 'Female'),
    ],
    ('CS-F', 6): [
        ('Nandini Gupta',   '6CS22CS001', 'nandini@college.com',  '9800000046', 'Female'),
        ('Naveen Kumar',    '6CS22CS002', 'naveen@college.com',   '9800000047', 'Male'),
        ('Niharika Joshi',  '6CS22CS003', 'niharika@college.com', '9800000048', 'Female'),
        ('Omkar Desai',     '6CS22CS004', 'omkar@college.com',    '9800000049', 'Male'),
        ('Pallavi Verma',   '6CS22CS005', 'pallavi@college.com',  '9800000050', 'Female'),
        ('Parth Malhotra',  '6CS22CS006', 'parth@college.com',    '9800000051', 'Male'),
        ('Pooja Saxena',    '6CS22CS007', 'pooja@college.com',    '9800000052', 'Female'),
        ('Pranesh Bhat',    '6CS22CS008', 'pranesh@college.com',  '9800000053', 'Male'),
        ('Priyanka Das',    '6CS22CS009', 'priyanka@college.com', '9800000054', 'Female'),
    ],
    ('CS-G', 6): [
        ('Rajesh Nair',     '6CS22CS010', 'rajesh@college.com',   '9800000055', 'Male'),
        ('Ramya Pillai',    '6CS22CS011', 'ramya@college.com',    '9800000056', 'Female'),
        ('Rohit Tiwari',    '6CS22CS012', 'rohit@college.com',    '9800000057', 'Male'),
        ('Roshni Kaur',     '6CS22CS013', 'roshni@college.com',   '9800000058', 'Female'),
        ('Sachin Patil',    '6CS22CS014', 'sachin@college.com',   '9800000059', 'Male'),
        ('Sandhya Menon',   '6CS22CS015', 'sandhya@college.com',  '9800000060', 'Female'),
        ('Sanjay Hegde',    '6CS22CS016', 'sanjay@college.com',   '9800000061', 'Male'),
        ('Shruti Agarwal',  '6CS22CS017', 'shruti@college.com',   '9800000062', 'Female'),
        ('Suresh Chopra',   '6CS22CS018', 'suresh@college.com',   '9800000063', 'Male'),
    ],
}

def get_working_days(n=30):
    days = []
    d = date.today()
    while len(days) < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            days.append(d)
    return days

working_days = get_working_days(30)

for (section, sem), students in all_students.items():
    class_id = classes[(section, sem)]
    sub_ids = subjects_by_sem.get(sem, [])

    for name, usn, email, phone, gender in students:
        cur.execute("""
            INSERT IGNORE INTO students (name, usn, email, phone, class_id, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, usn, email, phone, class_id, gender))
        conn.commit()

        cur.execute("SELECT id FROM students WHERE usn = %s", (usn,))
        row = cur.fetchone()
        if not row:
            continue
        student_id = row[0]

        # Marks
        for subject_id in sub_ids:
            marks = random.randint(45, 98)
            cur.execute("""
                INSERT IGNORE INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by)
                VALUES (%s, %s, 'semester', %s, 100, %s)
            """, (student_id, subject_id, marks, admin_id))

        # Attendance
        for subject_id in sub_ids:
            for day in working_days:
                status = 'present' if random.random() < 0.85 else 'absent'
                cur.execute("""
                    INSERT IGNORE INTO attendance (student_id, subject_id, date, status, marked_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, subject_id, day, status, admin_id))

        conn.commit()
        print(f"Added: {name} | {section} Sem{sem}")

cur.close()
conn.close()
print("\nDone! 63 students across 7 sections (Sem 2, 4, 6) with marks and attendance.")
