from models import get_db

def log_activity(user_id, action, table_affected=None, record_id=None, details=None):
    try:
        db = get_db()
        cur = db.connection.cursor()
        cur.execute("""
            INSERT INTO activity_logs (user_id, action, table_affected, record_id, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action, table_affected, record_id, details))
        db.connection.commit()
        cur.close()
    except Exception:
        pass  # Don't break main flow if logging fails
