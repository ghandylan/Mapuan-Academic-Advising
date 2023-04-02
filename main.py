from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship
from flask_login import *

my_app = Flask(__name__, template_folder='templates', static_folder='static')
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/academic_advising'
my_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
my_app.config['SECRET_KEY'] = 'secret HAHAHAHAH'
db = SQLAlchemy(my_app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(my_app)


@login_manager.user_loader
def load_user(student_number):
    return Student.query.get(student_number)


def load_admin(admin_number):
    return Admin.query.get(admin_number)


class Student(db.Model, UserMixin):
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

    def is_active(self):
        return True

    def get_id(self):
        return self.student_number

    def is_authenticated(self):
        return True


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    admin_number = db.Column(String(10), primary_key=True)
    admin_email = db.Column(String(255), nullable=False)
    admin_password = db.Column(String(255), nullable=False)
    admin_name = db.Column(String(255), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.admin_number

    def is_authenticated(self):
        return True


class Queue(db.Model, UserMixin):
    __tablename__ = 'queue'

    queue_id = db.Column(Integer, primary_key=True)

    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    student_name = db.Column(String(255), ForeignKey('student.student_name'), nullable=False)
    student_year = db.Column(String(255), ForeignKey('student.student_year'), nullable=False)
    student_program = db.Column(String(255), ForeignKey('student.student_program'), nullable=False)
    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    queue_status = db.Column(String(255), nullable=False)

    student = relationship("Student", backref="queues")
    admin = relationship("Admin", backref="queues")


class Feedback(db.Model, UserMixin):
    __tablename__ = 'feedback'

    feedback_id = db.Column(Integer, primary_key=True)
    feedback = db.Column(String(255), nullable=False)

    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    student = relationship("Student", backref="feedbacks")

    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="feedbacks")


class Class(db.Model, UserMixin):
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
    if request.method == 'POST':
        # GET THE EMAIL AND PASSWORD ON THE FORM
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            student = Student.query.filter_by(student_email=email, student_password=password).first()
            admin = Admin.query.filter_by(admin_email=email, admin_password=password).first()
            if student:
                session['user_id'] = student.student_number
                login_user(student, remember=True)
                return redirect(url_for('student_dashboard'))
            elif admin:
                session['admin_id'] = admin.admin_number
                login_user(admin, remember=True)
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password', 'warning')
                return redirect(url_for('login_page', error='Invalid email or password'))
        else:
            flash('Email and password are required', 'error')
            return redirect(url_for('login_page', error='Email and password are required'))

    return render_template('index.html')


@my_app.route('/student_dashboard')
def student_dashboard():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:
        user = Student.query.get(user_id)
        print(user.student_name)
        flash('Logged in successfully', 'success')
        return render_template('welcome.html', user=user, username=user.student_name)
    # if not logged in, redirect to login page
    else:
        return redirect(url_for('login'))


# FIXME: greeting message not showing
@my_app.route('/admin_dashboard')
def admin_dashboard():
    # check if user is logged in
    user_id = session.get('admin_id')
    if user_id:
        user = Admin.query.get(user_id)
        print(user.admin_name)
        flash('Logged in successfully', 'success')
        return render_template('welcome.html', user=user, username=user.admin_name)
    else:
        return redirect(url_for('login'))


@my_app.route('/login_page')
def login_page():
    #     show error message if login failed
    error = request.args.get('error')
    return render_template('index.html', error=error)


@my_app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
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


# def get_queue_list():


if __name__ == "__main__":
    my_app.run(debug=True)
    my_app.run(threaded=True, processes=100)
    db.create_all()
