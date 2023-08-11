from flask import Blueprint, redirect, url_for, request, render_template, flash
from sqlalchemy import asc

from models import db, Student, Admin, Queue
from flask_login import login_user, current_user, login_required, logout_user

defaultview = Blueprint('defaultview', __name__)


@defaultview.route('/')  # HOME PAGE
def index():
    return redirect(url_for('defaultview.login'))


@defaultview.route('/login', methods=['GET', 'POST'])  # LOGIN PAGE
def login():
    if request.method == 'POST':
        # GET THE EMAIL AND PASSWORD ON THE FORM
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            student = Student.query.filter_by(student_email=email, student_password=password).first()
            admin = Admin.query.filter_by(admin_email=email, admin_password=password).first()
            if student:
                print(f'Student {student.student_name} has logged in')
                login_user(student, remember=True)
                # check if student is already in queue
                queue = Queue.query.filter_by(admin_id=student.queue_ID).first()
                if queue:
                    return redirect(url_for('waiting_page'))
                else:
                    return redirect(url_for('student_dashboard'))
            elif admin:
                login_user(admin, remember=True)
                admin.status = 'Online'
                db.session.commit()
                print(f'Admin {admin.admin_name} has logged in')
                print(f'Admin {admin.admin_name} is online')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password', 'warning')
                return redirect(url_for('defaultview.login', error='Invalid email or password'))
        else:
            flash('Email and password are required', 'error')
            return redirect(url_for('login_page', error='Email and password are required'))

    return render_template('login.html')


@defaultview.route('/login_page')  # LOGIN PAGE
def login_page():
    #     show error message if login failed
    error = request.args.get('error')
    return render_template('login.html', error=error)


@defaultview.route('/logout', methods=['GET', 'POST'])  # LOGOUT
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
        current_user.sms_sent = False
        db.session.commit()

        print(f"Student {current_user.student_name} logged out")

    db.session.commit()
    logout_user()

    flash('Logged out successfully', 'success')
    return redirect(url_for('default_view.login_page'))
