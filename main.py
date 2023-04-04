from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask_login import *
from sqlalchemy.orm import *
from twilio.rest import Client

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


class Queue(db.Model):
    queue_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_number = db.Column(db.String(10), db.ForeignKey('student.student_number'), nullable=False)
    student_name = db.Column(db.String(255), db.ForeignKey('student.student_name'), nullable=False)
    student_year = db.Column(db.String(255), db.ForeignKey('student.student_year'), nullable=False)
    student_program = db.Column(db.String(255), db.ForeignKey('student.student_program'), nullable=False)
    admin_number = db.Column(db.String(10), db.ForeignKey('admin.admin_number'), nullable=False)
    queue_status = db.Column(db.String(255), nullable=False)


class Feedback(db.Model, UserMixin):
    feedback_id = db.Column(Integer, primary_key=True, autoincrement=True)
    feedback = db.Column(String(255), nullable=False)
    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    student = relationship("Student", backref="feedbacks")
    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="feedbacks")


class Class(db.Model, UserMixin):
    class_id = db.Column(Integer, primary_key=True)
    class_name = db.Column(String(255), nullable=False)
    class_code = db.Column(String(255), nullable=False)
    teacher_name = db.Column(String(255), nullable=False)
    admin_number = db.Column(String(10), ForeignKey('admin.admin_number'), nullable=False)
    admin = relationship("Admin", backref="classes")


@my_app.route('/')  # HOME PAGE
def index():
    return redirect(url_for('login'))


@my_app.route('/login', methods=['GET', 'POST'])  # LOGIN PAGE
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


@my_app.route('/student_dashboard')  # STUDENT VIEW
def student_dashboard():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:
        user = Student.query.get(user_id)
        # queue = Queue.query.filter_by(student_number=user_id).all()

        # queue_std_name = Queue.query.filter_by(student_name=user_id).first()
        # queue_std_year = Queue.query.filter_by(student_year=user_id).first()
        # queue_std_program = Queue.query.filter_by(student_program=user_id).first()
        # queue_status = Queue.query.filter_by(queue_status=user_id).first()
        print(user.student_name)
        # print(queue)
        flash('Logged in successfully', 'success')
        return render_template('welcome.html', user=user, username=user.student_name)
    # if not logged in, redirect to login page
    else:
        return redirect(url_for('login'))


@my_app.route('/admin_dashboard')  # ADMIN VIEW
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


@my_app.route('/student_register', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
def student_register():
    if request.method == 'POST':
        # GET THE EMAIL AND PASSWORD ON THE FORM
        student_number = request.form.get('student_number')
        student_name = request.form.get('student_name')
        student_email = request.form.get('student_email')
        student_password = request.form.get('student_password')
        student_year = request.form.get('student_year')
        student_program = request.form.get('student_program')

        if student_number and student_name and student_email and student_password and student_year and student_program:
            queue = Queue(student_number=student_number, student_name=student_name, student_email=student_email)
            db.session.add(student)
            db.session.commit()
            flash('Student registered successfully', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('All fields are required', 'error')
            return redirect(url_for('student_register'))
    return render_template('advising.html')


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


@my_app.route('/send_sms')
def send_sms():
    # Replace with your Twilio account SID and auth token
    account_sid = 'AC63f05ab5b2848020c4cc50a103a01112'
    auth_token = 'cbc2daa0204f4c6492f4ad99cdd3d7d2'

    # Replace with your Twilio phone number and recipient phone number
    from_phone_number = '+15854886256'
    to_phone_number = '+639616220682'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Send the SMS message
    message = client.messages.create(
        body='Uy Dylan, this is a test message from the Mapua Academic Advising!',
        from_=from_phone_number,
        to=to_phone_number
    )

    # Return a response to the user
    return f'SMS message sent to {to_phone_number}: {message.sid}'


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
    my_app.run(threaded=True, processes=100)
    db.create_all()
