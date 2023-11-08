from flask import Flask
from flask_login import LoginManager
from models import db
from config import Config
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from models import Admin, Student
    login_manager = LoginManager()
    login_manager.login_view = 'defaultview.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        student = Student.query.filter_by(student_number=user_id).first()
        admin = Admin.query.filter_by(admin_number=user_id).first()
        if student:
            return student
        elif admin:
            return admin
        else:
            return None

    from blueprints.studentview import studentview
    app.register_blueprint(studentview)

    from blueprints.adminview import adminview
    app.register_blueprint(adminview)

    from blueprints.defaultview import defaultview
    app.register_blueprint(defaultview)

    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    db.init_app(app)

    return app


app_instance = create_app()
if __name__ == "__main__":
    app_instance.run(debug=True)
