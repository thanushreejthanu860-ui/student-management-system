from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import get_db
from utils.excel_handler import process_excel_upload, export_students_excel
from utils.pdf_generator import generate_report_card
from utils.logger import log_activity
import os

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/upload-excel', methods=['POST'])
@jwt_required()
def upload_excel():
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod', 'faculty'):
        return jsonify({'error': 'Access denied'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    upload_type = request.form.get('type', 'marks')

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Only Excel files allowed'}), 400

    from config import Config
    filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        result = process_excel_upload(filepath, upload_type, int(get_jwt_identity()))
        log_activity(int(get_jwt_identity()), f'upload_excel_{upload_type}', details=file.filename)
        return jsonify({'message': 'Upload successful', 'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@reports_bp.route('/export-excel', methods=['GET'])
@jwt_required()
def export_excel():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id required'}), 400

    filepath = export_students_excel(int(class_id))
    return send_file(filepath, as_attachment=True, download_name='students_report.xlsx')


@reports_bp.route('/report-card/<int:student_id>', methods=['GET'])
@jwt_required()
def report_card(student_id):
    filepath = generate_report_card(student_id)
    if not filepath:
        return jsonify({'error': 'Could not generate report card'}), 404
    return send_file(filepath, as_attachment=True, download_name=f'report_card_{student_id}.pdf')


@reports_bp.route('/assign-faculty', methods=['POST'])
@jwt_required()
def assign_faculty():
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod'):
        return jsonify({'error': 'Admin or HOD access required'}), 403

    data = request.get_json()
    if not all(data.get(f) for f in ['faculty_id', 'subject_id', 'class_id', 'academic_year']):
        return jsonify({'error': 'faculty_id, subject_id, class_id, academic_year required'}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            INSERT INTO faculty_assignments (faculty_id, subject_id, class_id, academic_year)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE faculty_id=%s
        """, (data['faculty_id'], data['subject_id'], data['class_id'],
              data['academic_year'], data['faculty_id']))
        conn.commit()
        log_activity(int(get_jwt_identity()), 'assign_faculty', 'faculty_assignments',
                     cur.lastrowid, f"Faculty {data['faculty_id']} → Subject {data['subject_id']}")
        return jsonify({'message': 'Faculty assigned successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@reports_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.name, u.email, r.role_name as role, u.is_active
        FROM users u JOIN roles r ON u.role_id = r.id
        WHERE r.role_name IN ('hod', 'faculty')
        ORDER BY r.role_name, u.name
    """)
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'users': users}), 200


@reports_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    from routes.auth import auth_bp
    import bcrypt
    data = request.get_json()
    if not all(data.get(f) for f in ['name', 'email', 'password', 'role']):
        return jsonify({'error': 'All fields required'}), 400
    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM roles WHERE role_name = %s", (data['role'],))
        role = cur.fetchone()
        if not role:
            return jsonify({'error': 'Invalid role'}), 400
        cur.execute("INSERT INTO users (name, email, password, role_id) VALUES (%s, %s, %s, %s)",
                    (data['name'], data['email'], hashed, role['id']))
        conn.commit()
        return jsonify({'message': 'User created', 'id': cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@reports_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': 'User deactivated'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@reports_bp.route('/admin/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.id, s.subject_name, s.subject_code, s.semester, d.name as department
        FROM subjects s JOIN departments d ON s.department_id = d.id
        ORDER BY s.subject_name
    """)
    subjects = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'subjects': subjects}), 200


@reports_bp.route('/admin/classes', methods=['GET'])
@jwt_required()
def get_classes():
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod'):
        return jsonify({'error': 'Access required'}), 403
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.id, c.class_name, c.semester, c.academic_year, d.name as department
        FROM classes c JOIN departments d ON c.department_id = d.id
        ORDER BY c.class_name
    """)
    classes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'classes': classes}), 200


@reports_bp.route('/admin/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT fa.id, u.name as faculty_name, r.role_name as role,
               s.subject_name, s.subject_code, c.class_name, fa.academic_year
        FROM faculty_assignments fa
        JOIN users u ON fa.faculty_id = u.id
        JOIN roles r ON u.role_id = r.id
        JOIN subjects s ON fa.subject_id = s.id
        JOIN classes c ON fa.class_id = c.id
        ORDER BY fa.academic_year DESC, u.name
    """)
    assignments = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'assignments': assignments}), 200


@reports_bp.route('/admin/assignments/<int:assignment_id>', methods=['DELETE'])
@jwt_required()
def delete_assignment(assignment_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM faculty_assignments WHERE id = %s", (assignment_id,))
        conn.commit()
        return jsonify({'message': 'Assignment removed'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()


@reports_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) as total FROM students")
    total_students = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM users WHERE role_id = (SELECT id FROM roles WHERE role_name='faculty')")
    total_faculty = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM subjects")
    total_subjects = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM classes")
    total_classes = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(DISTINCT student_id) as at_risk FROM (
            SELECT student_id,
                   ROUND(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct
            FROM attendance GROUP BY student_id, subject_id
            HAVING pct < 75
        ) t
    """)
    at_risk = cur.fetchone()['at_risk']

    cur.execute("""
        SELECT l.action, u.name, l.created_at
        FROM activity_logs l JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC LIMIT 10
    """)
    recent_activity = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        'students_at_risk': at_risk,
        'recent_activity': [dict(a) for a in recent_activity]
    }), 200


@reports_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM notifications
        WHERE is_read = FALSE
        ORDER BY created_at DESC LIMIT 50
    """)
    notifications = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'notifications': notifications}), 200
