import sqlalchemy
from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship

my_app = Flask(__name__, template_folder='templates', static_folder='static')
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/academic_advising'
my_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(my_app)


class Student(db.Model):
    __tablename__ = 'student'

    student_number = db.Column(String(10), primary_key=True)
    student_email = db.Column(String(255), nullable=False)
    student_password = db.Column(String(255), nullable=False)
    student_name = db.Column(String(255), nullable=False)
    student_contact_no = db.Column(String(255), nullable=False)
    student_program = db.Column(String(255), nullable=False)
    student_year = db.Column(String(255), nullable=False)
    student_concern = db.Column(String(255), nullable=False)

    class_id = db.Column(Integer, ForeignKey('class.class_id'), nullable=False)
    class_ = relationship("Class", backref="students")

    # is_student = db.Column(Boolean, nullable=False)


class Admin(db.Model):
    __tablename__ = 'admin'

    admin_number = db.Column(String(10), primary_key=True)
    admin_email = db.Column(String(255), nullable=False)
    admin_password = db.Column(String(255), nullable=False)
    admin_name = db.Column(String(255), nullable=False)

    # is_admin = db.Column(Boolean, nullable=False)


class Queue(db.Model):
    __tablename__ = 'queue'

    queue_id = db.Column(Integer, primary_key=True)
    queue_status = db.Column(String(255), nullable=False)

    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    student = relationship("Student", backref="queues")

    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="queues")


class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_id = db.Column(Integer, primary_key=True)
    feedback = db.Column(String(255), nullable=False)

    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    student = relationship("Student", backref="feedbacks")

    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="feedbacks")


class Class(db.Model):
    __tablename__ = 'class'

    class_id = db.Column(Integer, primary_key=True)
    class_name = db.Column(String(255), nullable=False)
    class_code = db.Column(String(255), nullable=False)
    teacher_name = db.Column(String(255), nullable=False)

    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="classes")


def establish_session(engine):
    session = sqlalchemy.orm.sessionmaker()
    session.configure(bind=engine)
    return session()


@my_app.route('/', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    student = Student.query.filter_by(student_email=email, student_password=password).first()
    if student and student.is_student == 1:
        # User is a student
        # Do something with the student object
        return 'Welcome, student!'

    admin = Admin.query.filter_by(admin_email=email, admin_password=password).first()
    if admin and not admin.is_student == 1:
        # User is an admin
        # Do something with the admin object
        return 'Welcome, admin!'

    print(email, password)
    return render_template('index.html')


@my_app.route('/logout')
def logout():
    return "Logout"


@my_app.route('/test', methods=['GET'])
def test():
    student = Student.query.all()
    admin = Admin.query.all()
    return student, admin


if __name__ == "__main__":
    my_app.run(debug=True)
    my_app.run()
    db.create_all()
