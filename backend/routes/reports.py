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
    upload_type = request.form.get('type', 'marks')  # marks or students or attendance

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
    required = ['faculty_id', 'subject_id', 'class_id', 'academic_year']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'faculty_id, subject_id, class_id, academic_year required'}), 400

    db = get_db()
    cur = db.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO faculty_assignments (faculty_id, subject_id, class_id, academic_year)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE faculty_id=%s
        """, (data['faculty_id'], data['subject_id'], data['class_id'],
              data['academic_year'], data['faculty_id']))
        db.connection.commit()
        log_activity(int(get_jwt_identity()), 'assign_faculty', 'faculty_assignments',
                     cur.lastrowid, f"Faculty {data['faculty_id']} → Subject {data['subject_id']}")
        return jsonify({'message': 'Faculty assigned successfully'}), 201
    except Exception as e:
        db.connection.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()


@reports_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    db = get_db()
    cur = db.connection.cursor()

    cur.execute("SELECT COUNT(*) as total FROM students")
    total_students = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM users WHERE role_id = (SELECT id FROM roles WHERE role_name='faculty')")
    total_faculty = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM subjects")
    total_subjects = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM classes")
    total_classes = cur.fetchone()['total']

    # Students with attendance < 75%
    cur.execute("""
        SELECT COUNT(DISTINCT student_id) as at_risk
        FROM (
            SELECT student_id,
                   ROUND(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct
            FROM attendance GROUP BY student_id, subject_id
            HAVING pct < 75
        ) t
    """)
    at_risk = cur.fetchone()['at_risk']

    # Recent activity logs
    cur.execute("""
        SELECT l.action, u.name, l.created_at
        FROM activity_logs l JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC LIMIT 10
    """)
    recent_activity = cur.fetchall()
    cur.close()

    return jsonify({
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        'students_at_risk': at_risk,
        'recent_activity': recent_activity
    }), 200


@reports_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    db = get_db()
    cur = db.connection.cursor()
    cur.execute("""
        SELECT * FROM notifications
        WHERE is_read = FALSE
        ORDER BY created_at DESC LIMIT 50
    """)
    notifications = cur.fetchall()
    cur.close()
    return jsonify({'notifications': notifications}), 200
