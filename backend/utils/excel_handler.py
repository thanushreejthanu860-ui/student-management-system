import pandas as pd
from models import get_db
from config import Config
import os

def process_excel_upload(filepath, upload_type, uploaded_by):
    df = pd.read_excel(filepath)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    inserted = 0
    errors = []

    try:
        if upload_type == 'students':
            for i, row in df.iterrows():
                try:
                    cur.execute("""
                        INSERT INTO students (name, usn, email, phone, class_id, gender)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE name=%s, email=%s
                    """, (row['name'], row['usn'], row.get('email'), row.get('phone'),
                          row['class_id'], row.get('gender'),
                          row['name'], row.get('email')))
                    inserted += 1
                except Exception as e:
                    errors.append(f"Row {i+2}: {str(e)}")

        elif upload_type == 'marks':
            for i, row in df.iterrows():
                try:
                    cur.execute("SELECT id FROM students WHERE usn = %s", (row['usn'],))
                    student = cur.fetchone()
                    cur.execute("SELECT id, max_marks FROM subjects WHERE subject_code = %s", (row['subject_code'],))
                    subject = cur.fetchone()

                    if student and subject:
                        cur.execute("""
                            INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE marks_obtained=%s
                        """, (student['id'], subject['id'], row['exam_type'],
                              row['marks_obtained'], row.get('max_marks', subject['max_marks']),
                              uploaded_by, row['marks_obtained']))
                        inserted += 1
                    else:
                        errors.append(f"Row {i+2}: Student or subject not found")
                except Exception as e:
                    errors.append(f"Row {i+2}: {str(e)}")

        elif upload_type == 'attendance':
            for i, row in df.iterrows():
                try:
                    cur.execute("SELECT id FROM students WHERE usn = %s", (row['usn'],))
                    student = cur.fetchone()
                    cur.execute("SELECT id FROM subjects WHERE subject_code = %s", (row['subject_code'],))
                    subject = cur.fetchone()

                    if student and subject:
                        cur.execute("""
                            INSERT INTO attendance (student_id, subject_id, date, status, marked_by)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE status=%s
                        """, (student['id'], subject['id'], row['date'], row['status'],
                              uploaded_by, row['status']))
                        inserted += 1
                    else:
                        errors.append(f"Row {i+2}: Student or subject not found")
                except Exception as e:
                    errors.append(f"Row {i+2}: {str(e)}")

        conn.commit()
    finally:
        cur.close()
        conn.close()

    return {'inserted': inserted, 'errors': errors}


def export_students_excel(class_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT s.usn, s.name, s.email, s.phone, s.gender,
               c.class_name, c.semester,
               ROUND(SUM(m.marks_obtained) * 100.0 / SUM(m.max_marks), 2) as percentage
        FROM students s
        JOIN classes c ON s.class_id = c.id
        LEFT JOIN marks m ON s.id = m.student_id
        WHERE s.class_id = %s
        GROUP BY s.id, s.usn, s.name, s.email, s.phone, s.gender, c.class_name, c.semester
        ORDER BY percentage DESC
    """, (class_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    df = pd.DataFrame(data)
    filepath = os.path.join(Config.REPORTS_FOLDER, f'class_{class_id}_report.xlsx')
    df.to_excel(filepath, index=False)
    return filepath
