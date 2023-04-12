import os

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
    student_concern = db.Column(String(255))
    student_additional_comment = db.Column(String(255))

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
    available = db.Column(Boolean, nullable=False, default=True)

    def is_active(self):
        return True

    def get_id(self):
        return self.admin_number

    def is_authenticated(self):
        return True


class Queue(db.Model):
    queue_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_number = db.Column(db.String(10), db.ForeignKey('student.student_number'), nullable=False)
    admin_number = db.Column(db.String(10), db.ForeignKey('admin.admin_number'), nullable=False)
    queue_status = db.Column(db.String(255), nullable=False)
    zoom_link = db.Column(db.String(255))

    student = relationship("Student", backref="queues")
    admin = relationship("Admin", backref="queues")


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

    return render_template('login.html')


@my_app.route('/student_dashboard')  # STUDENT VIEW
def student_dashboard():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:
        user = Student.query.get(user_id)

        result = db.session.query(Queue.queue_ID, Student.student_number, Student.student_name, Student.student_program,
                                  Student.student_year, Queue.queue_status) \
            .join(Student, Queue.student_number == Student.student_number) \
            .all()

        # Pass the user and queue entries to the template
        return render_template('welcome.html', user=user, username=user.student_name, result=result)
    # if not logged in, redirect to login page
    else:
        return redirect(url_for('login'))


@my_app.route('/admin_dashboard')  # ADMIN VIEW
def admin_dashboard():
    # TODO: continue working on admin side, GOOD LUCK!
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
    user_id = session.get('user_id')
    if user_id:
        user = Student.query.get(user_id)
        if request.method == 'POST':
            # get the data from dropdown(concern) and text area(comments)
            concern = request.form.get('concerns')  # dropdown
            concerns = request.form.get('concern')  # text area

            # update the student table with the new concern and comments
            user.student_concern = concern
            user.student_additional_comment = concerns

            # push the new data to the database
            db.session.commit()

            # loop through the admin rows and find the first available admin then assign its primary key to the queue
            admin = Admin.query.filter_by(available=1).first()
            if admin:
                # update the admin table to set the admin to unavailable
                admin.available = 0
                db.session.commit()

            queue = Queue()

            queue.student_number = user.student_number
            queue.admin_number = admin.admin_number
            queue.queue_status = 'Waiting'
            queue.zoom_link = 'https://zoom.us/j/94678770175?pwd=Qm5wMG5XMHAwL3NudC9yb3E4R0xUZz09'

            db.session.add(queue)
            db.session.commit()

            # count the number of entries in the queue
            total_queue_entries = Queue.query.count()
            adviser_in_charge = admin.admin_name
            zoom_link = queue.zoom_link

            # FIXME: make SMS more personalized, refer to send_sms function
            formatted_number = '+' + user.student_contact_no
            send_sms(formatted_number)

            return render_template('student/zoom.html', user=user, total_queue_entries=total_queue_entries,
                                   adviser_in_charge=adviser_in_charge, zoom_link=zoom_link, username=user.student_name)

        return render_template('student/advising.html', user=user)
    return render_template('student/advising.html')


@my_app.route('/login_page')
def login_page():
    #     show error message if login failed
    error = request.args.get('error')
    return render_template('login.html', error=error)


@my_app.route('/logout')
@login_required
def logout():
    #  remove user from QUEUE table and make the admin available
    user_id = session.get('user_id')
    # if queue table is empty, do not delete the row
    if Queue.query.count() == 0:
        logout_user()
    else:
        if user_id:
            user = Student.query.get(user_id)
            queue = Queue.query.filter_by(student_number=user.student_number).first()
            admin = Admin.query.get(queue.admin_number)
            admin.available = 1
            db.session.delete(queue)
            db.session.commit()
            logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login_page'))


def send_sms(to_phone_number):
    # Replace with your Twilio account SID and auth token
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    # Replace with your Twilio phone number and recipient phone number
    from_phone_number = os.environ.get('TWILIO_FROM_PHONE_NUMBER')
    # to_phone_number = '+639616220682'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # FIXME: make SMS more personalized
    # Send the SMS message
    message = client.messages.create(
        body='Uy pare, this is a test message from the Mapua Academic Advising!',
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
