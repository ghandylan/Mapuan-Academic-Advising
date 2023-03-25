from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
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


@my_app.route('/')
def index():
    return redirect(url_for('login'))


@my_app.route('/login', methods=['GET', 'POST'])
def login():
    if request == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Student.query.filter_by(student_email=email).first()

        if user is not None and user.student_password == password:
            session['student_number'] = user.student_number
            if user.is_student:
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            admin = Admin.query.filter_by(admin_email=email).first()
            if admin is not None and admin.admin_password == password:
                session['admin_number'] = admin.admin_number
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template(index.html, error='Invalid email or password')
    else:
        return render_template('index.html')


@my_app.route('/student_dashboard')
def student_dashboard():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:
        user = Student.query.get(user_id)
        return render_template('welcome.html', user=user)
    # if not logged in, redirect to login page
    else:
        return redirect(url_for('login'))


@my_app.route('/admin_dashboard')
def admin_dashboard():
    # check if user is logged in
    admin_id = session.get('admin_id')
    if admin_id:
        admin = Admin.query.get(admin_id)
        return render_template('welcome.html', admin=admin)
    # if not logged in, redirect to login page
    else:
        return redirect(url_for('login'))


@my_app.route('/login_page')
def login_page():
    #     show error message if login failed
    error = request.args.get('error')
    return render_template('index.html', error=error)


@my_app.route('/logout')
def logout():
    # remove the user from the session
    session.pop('user', None)
    return redirect(url_for('login_page'))


@my_app.route('/test', methods=['GET'])
def test():
    students = Student.query.all()
    student_list = []
    for student in students:
        student_dict = {
            'student_number': student.student_number,
            'student_email': student.student_email,
            'student_password': student.student_password,
            'student_name': student.student_name,
            'student_contact_no': student.student_contact_no,
            'student_program': student.student_program,
            'student_year': student.student_year,
            'student_concern': student.student_concern,
            'class_ID': student.class_id,
        }
        student_list.append(student_dict)
    return jsonify(student_list)


if __name__ == "__main__":
    my_app.run(debug=True)
    my_app.run()
    db.create_all()
