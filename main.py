import os
import vonage  # sms API

from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from flask_login import *
from sqlalchemy.orm import *  # object relational mapper
from twilio.rest import Client  # sms API
from flask_socketio import SocketIO  # live update

my_app = Flask(__name__, template_folder='templates', static_folder='static')
socketio = SocketIO(my_app)
my_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/academic_advising'
my_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
my_app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(my_app)
my_app.config['SESSION_TYPE'] = 'filesystem'
Session(my_app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(my_app)


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
    queue_order = db.Column(Integer)
    queue_status = db.Column(String(255))
    is_admin = db.Column(Boolean, nullable=False, default=False)

    queue_ID = db.Column(Integer, ForeignKey('queue.queue_ID'))
    queue = relationship("Queue", backref="students")

    def is_active(self):
        return True

    def get_id(self):
        return self.student_number

    def is_authenticated(self):
        return True


class Admin(db.Model, UserMixin):
    admin_id = db.Column(Integer, primary_key=True, autoincrement=True)
    admin_number = db.Column(String(10))
    admin_email = db.Column(String(255), nullable=False)
    admin_password = db.Column(String(255), nullable=False)
    admin_name = db.Column(String(255), nullable=False)
    available = db.Column(Boolean, nullable=False, default=True)
    zoom_link = db.Column(String(255))
    status = db.Column(String(255))
    is_admin = db.Column(Boolean, nullable=False, default=True)

    def is_active(self):
        return True

    def get_id(self):
        return self.admin_number

    def is_authenticated(self):
        return True


class Queue(db.Model, UserMixin):
    queue_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    queue_status = db.Column(db.String(255), nullable=False)

    admin = relationship("Admin", backref="queues")


class Feedback(db.Model, UserMixin):
    feedback_id = db.Column(Integer, primary_key=True, autoincrement=True)
    feedback = db.Column(String(255), nullable=False)
    student_number = db.Column(String(10), ForeignKey('student.student_number'), nullable=False)
    rating = db.Column(String(255), nullable=False)
    admin_id = db.Column(Integer, ForeignKey('admin.admin_id'), nullable=False)
    date = db.Column(String(255), nullable=False)

    student = relationship("Student", backref="feedbacks")
    admin = relationship("Admin", backref="feedbacks")


class Class(db.Model, UserMixin):
    class_id = db.Column(Integer, primary_key=True)
    class_name = db.Column(String(255), nullable=False)
    class_code = db.Column(String(255), nullable=False)
    teacher_name = db.Column(String(255), nullable=False)
    admin_id = db.Column(Integer, ForeignKey('admin.admin_id'), nullable=False)

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
                print(f'Student {student.student_name} has logged in')

                login_user(student, remember=True)
                # check is studeent is already in queue
                queue = Queue.query.filter_by(admin_id=student.queue_ID).first()
                if queue:
                    return redirect(url_for('waiting_page'))
                else:
                    return redirect(url_for('student_dashboard'))
            elif admin:
                session['admin_id'] = admin.admin_id
                login_user(admin, remember=True)
                admin.status = 'Online'
                db.session.commit()
                print(f'Admin {admin.admin_name} has logged in')
                print(f'Admin {admin.admin_name} is online')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password', 'warning')
                return redirect(url_for('login_page', error='Invalid email or password'))
        else:
            flash('Email and password are required', 'error')
            return redirect(url_for('login_page', error='Email and password are required'))

    return render_template('login.html')


@my_app.route('/student_dashboard', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
def student_dashboard():
    # check if user is logged in
    user_id = session.get('user_id')
    if user_id:

        user = Student.query.get(user_id)
        # count the number of students with the Queue_ID 1
        queue_count = Queue.query.filter_by(admin_id=user_id).count()

        admins = Admin.query.all()
        for admin in admins:
            admin.queue_count = len(admin.queues[0].students)

        # get the selected admin from the form
        admin_id = request.form.get('admin_id')
        if request.method == 'POST':
            # get the name of the selected admin from the database
            admin_name = Admin.query.filter_by(admin_id=admin_id).first().admin_name
            #  save the selected admin to the database of the student
            user.queue_ID = admin_id
            # get the highest queue order number in the student table
            queue_order = db.session.query(func.max(Student.queue_order)).filter(Student.queue_ID == admin_id).scalar()
            db.session.commit()
            # if queue order is null, zero, or empty, or if user set the queue order to 1.
            if queue_order is None or queue_order == 0:
                user.queue_order = 1
                user.queue_status = 'Waiting'
                db.session.commit()
            else:
                # get the highest queue order number in the student table
                highest_queue_order = db.session.query(func.max(Student.queue_order)).filter(
                    Student.queue_ID == admin_id).scalar()
                # add 1 to the highest queue order number
                user.queue_order = highest_queue_order + 1
                user.queue_status = 'Waiting'
                db.session.commit()

            return render_template('student/advising.html',
                                   user=user,
                                   username=user.student_name,
                                   admins=admins,
                                   queue_count=queue_count,
                                   admin_id=admin_id,
                                   admin_name=admin_name)
        return render_template('student/enqueue.html',
                               user=user,
                               username=user.student_name,
                               admins=admins,
                               queue_count=queue_count)


@my_app.route('/student_register', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
def student_register():
    user_id = session.get('user_id')
    user = Student.query.get(user_id)
    concern = request.form.get('concerns')  # dropdown
    concerns = request.form.get('concern')  # text area
    adviser_in_charge = Admin.query.filter_by(admin_id=user.queue_ID).first().admin_name
    queue_count = Student.query.filter_by(queue_ID=user.queue_ID).count()
    zoom_link = Admin.query.filter_by(admin_id=user.queue_ID).first().zoom_link

    user.student_concern = concern
    user.student_additional_comment = concerns
    queue_order = user.queue_order
    queue_status = user.queue_status

    db.session.commit()

    if user_id:
        if request.method == 'POST':
            newline = '\n'
            formatted_number = '+' + user.student_contact_no

            message = f'Hi {user.student_name}, you are now in the queue. Your adviser is {adviser_in_charge}.{newline}Here is your zoom link:{newline}{zoom_link} {newline}Please wait for your turn and do not close the page. {newline}Thank you!'

            send_sms_vonage(formatted_number, message)
            return redirect(url_for('waiting_page'))

    return jsonify(queue_count=queue_count, queue_order=queue_order, queue_status=queue_status)


@my_app.route('/waiting_page', methods=['GET', 'POST'])  # STUDENT VIEW
def waiting_page():
    user_id = session.get('user_id')
    user = Student.query.get(user_id)

    adviser_in_charge = Admin.query.filter_by(admin_id=user.queue_ID).first().admin_name
    queue_count = Student.query.filter_by(queue_ID=user.queue_ID).count()
    zoom_link = Admin.query.filter_by(admin_id=user.queue_ID).first().zoom_link
    queue_order = user.queue_order

    return render_template('student/zoom.html',
                           user=user,
                           adviser_in_charge=adviser_in_charge,
                           username=user.student_name,
                           queue_count=queue_count,
                           queue_order=queue_order,
                           zoom_link=zoom_link)


@my_app.route('/get_queue_status')  # STUDENT VIEW
def get_queue_status():
    user_id = session.get('user_id')
    user = Student.query.get(user_id)
    queue_status = user.queue_status

    return jsonify(queue_status=queue_status)


@my_app.route('/feedback', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
def feedback():
    if request.method == 'POST':
        now = datetime.now()
        user_id = session.get('user_id')
        user = Student.query.get(user_id)

        student_number = user.student_number
        adviser = Admin.query.filter_by(admin_id=user.queue_ID).first()
        comments = request.form.get('comments')
        rating = request.form.get('rating')
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        student_feedback = Feedback(feedback=comments,
                                    student_number=student_number,
                                    rating=rating,
                                    admin_id=adviser.admin_id,
                                    date=date
                                    )

        user.student_concern = "Other"
        user.student_additional_comment = None
        user.queue_order = 0
        user.queue_status = None
        user.queue_ID = None
        db.session.add(student_feedback)
        db.session.commit()
        return redirect(url_for('exit_confirmation'))

    #     if user wants to log out

    return render_template('student/feedback.html')


@my_app.route('/faq', methods=['GET', 'POST'])  # STUDENT VIEW
def faq():
    return render_template('student/FAQ.html')


@my_app.route('/exit_confirmation', methods=['GET', 'POST'])  # STUDENT VIEW
def exit_confirmation():
    if request.method == 'POST':
        if 'Yes' in request.form:
            return redirect(url_for('student_dashboard'))
        else:
            return redirect(url_for('logout'))

    return render_template('student/exit_confirmation.html')


@my_app.route('/admin_dashboard', methods=['GET', 'POST'])  # ADMIN VIEW
def admin_dashboard():
    user_id = session.get('admin_id')
    user = Admin.query.get(user_id)
    students = db.session.query(Student).filter(Student.queue_ID == user_id).order_by(
        asc(Student.queue_order)).all()
    action = request.form.get('action', False)
    student_number = request.form.get('student_number', False)
    student = Student.query.filter_by(student_number=student_number).first()
    if user_id:
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return the updated data in JSON format
            return jsonify({'html': render_template('admin/Livelist-admin.html',
                                                    user=user,
                                                    username=user.admin_name,
                                                    students=students)})

        if action == 'check':
            student.queue_status = 'Fulfilled'
            if student.queue_order == 1:
                db.session.commit()
                # update queue order of all students in queue
                students = Student.query.filter(Student.queue_ID == user_id).all()
                for student in students:
                    student.queue_order = student.queue_order - 1
                db.session.commit()
            db.session.commit()
            print(student_number)

        elif action == 'delete':
            # perform delete action
            db.session.delete(student)
            # update queue order of all students in queue
            students = Student.query.filter(Student.queue_ID == user_id).all()
            for student in students:
                if student.queue_order > student.queue_order:
                    student.queue_order = student.queue_order - 1
            db.session.commit()
    return render_template('admin/Livelist-admin.html', user=user, username=user.admin_name, students=students)


@my_app.route('/edit_faq', methods=['GET', 'POST'])  # ADMIN VIEW
def edit_faq():
    return render_template('admin/FAQ-admin.html')


@my_app.route('/feedback_dashboard', methods=['GET', 'POST'])  # ADMIN VIEW
def feedback_dashboard():
    user_id = session.get('admin_id')
    user = Admin.query.get(user_id)

    excellent = db.session.query(Feedback).filter(Feedback.rating == "excellent").count()
    good = db.session.query(Feedback).filter(Feedback.rating == "good").count()
    fair = db.session.query(Feedback).filter(Feedback.rating == "ok").count()
    poor = db.session.query(Feedback).filter(Feedback.rating == "poor").count()
    terrible = db.session.query(Feedback).filter(Feedback.rating == "terrible").count()

    feedback_entries = Feedback.query.all()
    feedback_entries.reverse()

    feedbacks = Feedback.query.filter_by(admin_id=user_id).all()
    return render_template('admin/Feedback-admin.html',
                           user=user,
                           username=user.admin_name,
                           feedbacks=feedbacks,
                           excellent=excellent,
                           good=good,
                           fair=fair,
                           poor=poor,
                           terrible=terrible,
                           feedback_entries=feedback_entries)


@my_app.route('/update_zoom_link', methods=['POST'])  # ADMIN VIEW
def update_zoom_link():
    zoom_link = request.form['zoomLink']
    user_id = session.get('admin_id')
    user = Admin.query.get(user_id)
    user.zoom_link = zoom_link
    db.session.commit()
    return redirect(url_for('edit_zoom'))


@my_app.route('/edit_zoom')  # ADMIN VIEW
def edit_zoom():
    user_id = session.get('admin_id')
    user = Admin.query.get(user_id)
    admin_name = user.admin_name
    zoom_link = user.zoom_link
    status = user.status

    admins = Admin.query.all()

    return render_template('admin/editzoom-admin.html',
                           user=user,
                           username=admin_name,
                           zoom_link=zoom_link,
                           status=status,
                           admins=admins)


@my_app.route('/logout_warning', methods=['GET', 'POST'])  # ADMIN VIEW
def logout_warning():
    if request.method == 'POST':
        if request.form['warning'] == 'return':
            return redirect(url_for('admin_dashboard'))

    return render_template('admin/logout-warning.html')


@my_app.route('/login_page')  # LOGIN PAGE
def login_page():
    #     show error message if login failed
    error = request.args.get('error')
    return render_template('login.html', error=error)


@my_app.route('/logout', methods=['GET', 'POST'])  # LOGOUT
@login_required
def logout():
    if current_user.is_admin:
        students = db.session.query(Student).filter(Student.queue_ID == current_user.admin_id).order_by(
            asc(Student.queue_order)).count()
        if students > 0:
            flash('Please check all students before logging out', 'error')
            return redirect(url_for('logout_warning'))
        else:
            current_user.status = "Offline"
            print(f"Admin {current_user.admin_name} logged out")
    else:
        current_user.student_concern = "Other"
        current_user.student_additional_comment = ""
        current_user.queue_order = 0
        current_user.queue_status = ""
        current_user.queue_ID = None
        db.session.commit()

        print(f"Student {current_user.student_name} logged out")

    db.session.commit()
    logout_user()

    flash('Logged out successfully', 'success')
    return redirect(url_for('login_page'))


def sens_sms_twilio(to_phone_number, body):
    # Replace with your Twilio account SID and auth token
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    # Replace with your Twilio phone number and recipient phone number
    from_phone_number = os.environ.get('TWILIO_FROM_PHONE_NUMBER')
    # to_phone_number = '+639616220682'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    message = client.messages.create(body=body,
                                     from_=from_phone_number,
                                     to=to_phone_number)

    # Return a response to the user
    return f'SMS message sent to {to_phone_number}: {message.sid}'


def send_sms_vonage(to_phone_number, body):
    client = vonage.Client(key=os.environ.get('VONAGE_API_KEY'), secret=os.environ.get('VONAGE_API_SECRET'))
    sms = vonage.Sms(client)

    response_data = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": to_phone_number,
            "text": body
        }
    )

    if response_data["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {response_data['messages'][0]['error-text']}")


if __name__ == "__main__":
    socketio.run(my_app, debug=True, allow_unsafe_werkzeug=True)
    db.create_all()
