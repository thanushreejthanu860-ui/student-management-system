import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'student_mgmt')
    MYSQL_CURSORCLASS = 'DictCursor'

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
