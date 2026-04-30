from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import get_db
from utils.logger import log_activity
from utils.notifications import check_attendance_warning

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['POST'])
@jwt_required()
def add_marks():
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod', 'faculty'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not all(data.get(f) is not None for f in ['student_id', 'subject_id', 'exam_type', 'marks_obtained', 'max_marks']):
        return jsonify({'error': 'All fields required'}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE marks_obtained=%s, uploaded_by=%s
        """, (data['student_id'], data['subject_id'], data['exam_type'],
              data['marks_obtained'], data['max_marks'], int(get_jwt_identity()),
              data['marks_obtained'], int(get_jwt_identity())))
        conn.commit()
        return jsonify({'message': 'Marks saved'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@marks_bp.route('/marks/result/<int:student_id>', methods=['GET'])
@jwt_required()
def get_result(student_id):
    claims = get_jwt()
    user_id = int(get_jwt_identity())
    role = claims.get('role')
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Get student's class
    cur.execute("SELECT class_id FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()

    assigned_subjects = None
    if role in ('faculty', 'hod') and student:
        cur.execute("""
            SELECT subject_id FROM faculty_assignments
            WHERE faculty_id = %s AND class_id = %s
        """, (user_id, student['class_id']))
        rows = cur.fetchall()
        assigned_subjects = [r['subject_id'] for r in rows]

    if assigned_subjects is not None and len(assigned_subjects) > 0:
        fmt = ','.join(['%s'] * len(assigned_subjects))
        cur.execute(f"""
            SELECT sub.subject_name, sub.subject_code, sub.pass_marks,
                   SUM(m.marks_obtained) as total_obtained,
                   SUM(m.max_marks) as total_max
            FROM marks m
            JOIN subjects sub ON m.subject_id = sub.id
            WHERE m.student_id = %s AND m.subject_id IN ({fmt})
            GROUP BY sub.id, sub.subject_name, sub.subject_code, sub.pass_marks
        """, [student_id] + assigned_subjects)
    else:
        cur.execute("""
            SELECT sub.subject_name, sub.subject_code, sub.pass_marks,
                   SUM(m.marks_obtained) as total_obtained,
                   SUM(m.max_marks) as total_max
            FROM marks m
            JOIN subjects sub ON m.subject_id = sub.id
            WHERE m.student_id = %s
            GROUP BY sub.id, sub.subject_name, sub.subject_code, sub.pass_marks
        """, (student_id,))
    subject_marks = cur.fetchall()
    cur.close()
    conn.close()

    if not subject_marks:
        return jsonify({'error': 'No marks found'}), 404

    results = []
    overall_obtained = overall_max = 0

    for row in subject_marks:
        obtained = float(row['total_obtained'])
        maximum = float(row['total_max'])
        percentage = round((obtained / maximum) * 100, 2) if maximum > 0 else 0
        status = 'Pass' if obtained >= float(row['pass_marks']) else 'Fail'
        results.append({'subject': row['subject_name'], 'code': row['subject_code'],
                        'obtained': obtained, 'max': maximum, 'percentage': percentage, 'status': status})
        overall_obtained += obtained
        overall_max += maximum

    overall_percentage = round((overall_obtained / overall_max) * 100, 2) if overall_max > 0 else 0

    return jsonify({
        'student_id': student_id, 'subjects': results,
        'total_obtained': overall_obtained, 'total_max': overall_max,
        'overall_percentage': overall_percentage,
        'result': 'Pass' if all(r['status'] == 'Pass' for r in results) else 'Fail'
    }), 200


@marks_bp.route('/marks/ranks/all', methods=['GET'])
@jwt_required()
def get_all_ranks():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.id, s.name, s.usn, c.class_name, c.semester,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max,
               ROUND(SUM(m.marks_obtained) * 100.0 / SUM(m.max_marks), 2) as percentage
        FROM students s
        JOIN marks m ON s.id = m.student_id
        JOIN classes c ON s.class_id = c.id
        GROUP BY s.id, s.name, s.usn, c.class_name, c.semester
        ORDER BY percentage DESC
    """)
    students = cur.fetchall()
    cur.close()
    conn.close()
    rankings = [dict(s, rank=i+1) for i, s in enumerate(students)]
    return jsonify({'rankings': rankings}), 200


@marks_bp.route('/marks/ranks/<int:class_id>', methods=['GET'])
@jwt_required()
def get_ranks(class_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT s.id, s.name, s.usn,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max,
               ROUND(SUM(m.marks_obtained) * 100.0 / SUM(m.max_marks), 2) as percentage
        FROM students s
        JOIN marks m ON s.id = m.student_id
        WHERE s.class_id = %s
        GROUP BY s.id, s.name, s.usn
        ORDER BY percentage DESC
    """, (class_id,))
    students = cur.fetchall()
    cur.close()
    conn.close()

    rankings = [dict(s, rank=i+1) for i, s in enumerate(students)]
    return jsonify({'class_id': class_id, 'rankings': rankings}), 200


@marks_bp.route('/attendance', methods=['POST'])
@jwt_required()
def mark_attendance():
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod', 'faculty'):
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not all(data.get(f) for f in ['subject_id', 'date', 'records']):
        return jsonify({'error': 'subject_id, date, records required'}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        for record in data['records']:
            cur.execute("""
                INSERT INTO attendance (student_id, subject_id, date, status, marked_by)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status=%s, marked_by=%s
            """, (record['student_id'], data['subject_id'], data['date'],
                  record['status'], int(get_jwt_identity()),
                  record['status'], int(get_jwt_identity())))
        conn.commit()
        for record in data['records']:
            check_attendance_warning(record['student_id'], data['subject_id'])
        return jsonify({'message': f"Attendance marked for {len(data['records'])} students"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@marks_bp.route('/attendance/<int:student_id>', methods=['GET'])
@jwt_required()
def get_attendance(student_id):
    claims = get_jwt()
    user_id = int(get_jwt_identity())
    role = claims.get('role')
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Get student's class
    cur.execute("SELECT class_id FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()

    assigned_subjects = None
    if role in ('faculty', 'hod') and student:
        cur.execute("""
            SELECT subject_id FROM faculty_assignments
            WHERE faculty_id = %s AND class_id = %s
        """, (user_id, student['class_id']))
        rows = cur.fetchall()
        assigned_subjects = [r['subject_id'] for r in rows]

    if assigned_subjects is not None and len(assigned_subjects) > 0:
        fmt = ','.join(['%s'] * len(assigned_subjects))
        cur.execute(f"""
            SELECT sub.subject_name, sub.subject_code,
                   SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present_count,
                   COUNT(*) as total_classes,
                   ROUND(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage,
                   CASE WHEN ROUND(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) < 75
                        THEN 'WARNING' ELSE 'OK' END as attendance_status
            FROM attendance a
            JOIN subjects sub ON a.subject_id = sub.id
            WHERE a.student_id = %s AND a.subject_id IN ({fmt})
            GROUP BY sub.id, sub.subject_name, sub.subject_code
        """, [student_id] + assigned_subjects)
    else:
        cur.execute("""
            SELECT sub.subject_name, sub.subject_code,
                   SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present_count,
                   COUNT(*) as total_classes,
                   ROUND(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage,
                   CASE WHEN ROUND(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) < 75
                        THEN 'WARNING' ELSE 'OK' END as attendance_status
            FROM attendance a
            JOIN subjects sub ON a.subject_id = sub.id
            WHERE a.student_id = %s
            GROUP BY sub.id, sub.subject_name, sub.subject_code
        """, (student_id,))
    attendance = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({'student_id': student_id, 'attendance': attendance}), 200
