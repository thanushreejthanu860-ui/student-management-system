from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import get_db
from utils.logger import log_activity

students_bp = Blueprint('students', __name__)

def require_roles(*roles):
    claims = get_jwt()
    if claims.get('role') not in roles:
        return jsonify({'error': 'Access denied'}), 403
    return None

@students_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    claims = get_jwt()
    db = get_db()
    cur = db.connection.cursor()

    class_id = request.args.get('class_id')
    search = request.args.get('search', '')

    query = """
        SELECT s.id, s.name, s.usn, s.email, s.phone, s.gender,
               c.class_name, c.semester, d.name as department
        FROM students s
        JOIN classes c ON s.class_id = c.id
        JOIN departments d ON c.department_id = d.id
        WHERE (s.name LIKE %s OR s.usn LIKE %s)
    """
    params = [f'%{search}%', f'%{search}%']

    if class_id:
        query += " AND s.class_id = %s"
        params.append(class_id)

    # Faculty can only see their assigned classes
    if claims.get('role') == 'faculty':
        query += """ AND s.class_id IN (
            SELECT class_id FROM faculty_assignments WHERE faculty_id = %s
        )"""
        params.append(int(get_jwt_identity()))

    cur.execute(query, params)
    students = cur.fetchall()
    cur.close()
    return jsonify({'students': students, 'count': len(students)}), 200


@students_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    db = get_db()
    cur = db.connection.cursor()

    cur.execute("""
        SELECT s.*, c.class_name, c.semester, d.name as department
        FROM students s
        JOIN classes c ON s.class_id = c.id
        JOIN departments d ON c.department_id = d.id
        WHERE s.id = %s
    """, (student_id,))
    student = cur.fetchone()

    if not student:
        cur.close()
        return jsonify({'error': 'Student not found'}), 404

    # Get marks summary
    cur.execute("""
        SELECT sub.subject_name, sub.subject_code, m.exam_type,
               m.marks_obtained, m.max_marks
        FROM marks m
        JOIN subjects sub ON m.subject_id = sub.id
        WHERE m.student_id = %s
        ORDER BY sub.subject_name, m.exam_type
    """, (student_id,))
    marks = cur.fetchall()

    # Get attendance summary
    cur.execute("""
        SELECT sub.subject_name,
               SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) as present,
               COUNT(*) as total,
               ROUND(SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
        FROM attendance a
        JOIN subjects sub ON a.subject_id = sub.id
        WHERE a.student_id = %s
        GROUP BY sub.id, sub.subject_name
    """, (student_id,))
    attendance = cur.fetchall()
    cur.close()

    return jsonify({'student': student, 'marks': marks, 'attendance': attendance}), 200


@students_bp.route('/students', methods=['POST'])
@jwt_required()
def add_student():
    err = require_roles('admin', 'hod')
    if err: return err

    data = request.get_json()
    required = ['name', 'usn', 'class_id']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'name, usn, class_id required'}), 400

    db = get_db()
    cur = db.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO students (name, usn, email, phone, class_id, date_of_birth, gender, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['name'], data['usn'], data.get('email'), data.get('phone'),
              data['class_id'], data.get('date_of_birth'), data.get('gender'), data.get('address')))
        db.connection.commit()
        sid = cur.lastrowid
        log_activity(int(get_jwt_identity()), 'add_student', 'students', sid, f"Added student {data['usn']}")
        return jsonify({'message': 'Student added', 'id': sid}), 201
    except Exception as e:
        db.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()


@students_bp.route('/student/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    err = require_roles('admin', 'hod')
    if err: return err

    data = request.get_json()
    db = get_db()
    cur = db.connection.cursor()
    try:
        cur.execute("""
            UPDATE students SET name=%s, email=%s, phone=%s, gender=%s, address=%s
            WHERE id=%s
        """, (data.get('name'), data.get('email'), data.get('phone'),
              data.get('gender'), data.get('address'), student_id))
        db.connection.commit()
        log_activity(int(get_jwt_identity()), 'update_student', 'students', student_id)
        return jsonify({'message': 'Student updated'}), 200
    except Exception as e:
        db.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()


@students_bp.route('/student/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    err = require_roles('admin')
    if err: return err

    db = get_db()
    cur = db.connection.cursor()
    try:
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        db.connection.commit()
        log_activity(int(get_jwt_identity()), 'delete_student', 'students', student_id)
        return jsonify({'message': 'Student deleted'}), 200
    except Exception as e:
        db.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
