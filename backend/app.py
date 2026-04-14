from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from models import mysql

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # MySQL config
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB
    app.config['MYSQL_CURSORCLASS'] = Config.MYSQL_CURSORCLASS
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY

    mysql.init_app(app)
    JWTManager(app)

    # Register blueprints
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
