from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES

    CORS(app)
    JWTManager(app)

    from routes.auth import auth_bp
    from routes.students import students_bp
    from routes.marks import marks_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(students_bp, url_prefix='/api')
    app.register_blueprint(marks_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Student Management API running'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
