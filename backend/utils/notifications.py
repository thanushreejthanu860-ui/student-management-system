from models import get_db

def check_attendance_warning(student_id, subject_id):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT ROUND(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
            FROM attendance WHERE student_id = %s AND subject_id = %s
        """, (student_id, subject_id))
        result = cur.fetchone()

        if result and result['percentage'] is not None and float(result['percentage']) < 75:
            cur.execute("""
                SELECT id FROM notifications
                WHERE student_id = %s AND type = 'attendance_warning'
                AND DATE(created_at) = CURDATE()
            """, (student_id,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO notifications (student_id, message, type)
                    VALUES (%s, %s, 'attendance_warning')
                """, (student_id, f'Attendance below 75% for subject ID {subject_id}. Current: {result["percentage"]}%'))
                conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

def send_result_notification(student_id, result):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (student_id, message, type)
            VALUES (%s, %s, 'result')
        """, (student_id, f'Your result has been published. Overall: {result}'))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
