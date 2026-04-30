from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import bcrypt
from models import get_db
from utils.logger import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT u.id, u.name, u.email, u.password, u.is_active, r.role_name
        FROM users u JOIN roles r ON u.role_id = r.id
        WHERE u.email = %s
    """, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not user['is_active']:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(
        identity=str(user['id']),
        additional_claims={'role': user['role_name'], 'name': user['name']}
    )

    log_activity(user['id'], 'login', details=f"{user['role_name']} logged in")

    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role_name']}
    }), 200


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role_name = data.get('role')

    if not all([name, email, password, role_name]):
        return jsonify({'error': 'All fields required'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
        role = cur.fetchone()
        if not role:
            return jsonify({'error': 'Invalid role'}), 400

        cur.execute(
            "INSERT INTO users (name, email, password, role_id) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, role['id'])
        )
        user_id = cur.lastrowid
        conn.commit()
        log_activity(int(get_jwt_identity()), 'create_user', 'users', user_id, f"Created {role_name}: {email}")
        return jsonify({'message': 'User created', 'id': user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()
