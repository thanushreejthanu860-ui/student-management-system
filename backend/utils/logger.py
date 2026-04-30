from models import get_db

def log_activity(user_id, action, table_affected=None, record_id=None, details=None):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO activity_logs (user_id, action, table_affected, record_id, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action, table_affected, record_id, details))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
