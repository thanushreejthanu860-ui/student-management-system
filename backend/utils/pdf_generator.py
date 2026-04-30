from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from models import get_db
from config import Config
import os

def generate_report_card(student_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT s.name, s.usn, c.class_name, c.semester, d.name as department
        FROM students s
        JOIN classes c ON s.class_id = c.id
        JOIN departments d ON c.department_id = d.id
        WHERE s.id = %s
    """, (student_id,))
    student = cur.fetchone()

    if not student:
        cur.close()
        conn.close()
        return None

    cur.execute("""
        SELECT sub.subject_name, sub.subject_code, sub.pass_marks,
               SUM(m.marks_obtained) as obtained, SUM(m.max_marks) as maximum
        FROM marks m JOIN subjects sub ON m.subject_id = sub.id
        WHERE m.student_id = %s
        GROUP BY sub.id, sub.subject_name, sub.subject_code, sub.pass_marks
    """, (student_id,))
    marks = cur.fetchall()
    cur.close()
    conn.close()

    filepath = os.path.join(Config.REPORTS_FOLDER, f'report_{student_id}.pdf')
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("STUDENT REPORT CARD", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Name: {student['name']}  |  USN: {student['usn']}", styles['Normal']))
    elements.append(Paragraph(f"Class: {student['class_name']}  |  Semester: {student['semester']}  |  Dept: {student['department']}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Marks Table
    table_data = [['Subject', 'Code', 'Obtained', 'Max', 'Percentage', 'Status']]
    total_obtained = 0
    total_max = 0

    for row in marks:
        obtained = float(row['obtained'])
        maximum = float(row['maximum'])
        pct = round((obtained / maximum) * 100, 2) if maximum > 0 else 0
        status = 'Pass' if obtained >= float(row['pass_marks']) else 'Fail'
        table_data.append([row['subject_name'], row['subject_code'], obtained, maximum, f"{pct}%", status])
        total_obtained += obtained
        total_max += maximum

    overall_pct = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0
    table_data.append(['TOTAL', '', total_obtained, total_max, f"{overall_pct}%",
                       'Pass' if all(r[5] == 'Pass' for r in table_data[1:]) else 'Fail'])

    table = Table(table_data, colWidths=[150, 70, 60, 50, 70, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)

    doc.build(elements)
    return filepath
