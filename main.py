from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/academic_advising'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret'
    app.config['SESSION_TYPE'] = 'filesystem'

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

    db = SQLAlchemy(app)
    db.init_app(app)

    return app


app_instance = create_app()
if __name__ == "__main__":
    app_instance.run(debug=True)
