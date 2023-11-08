from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db, Student, Admin, Feedback, Queue
from rbac import role_required
from sms import send_sms_vonage

studentview = Blueprint('studentview', __name__)


def redirect_if_authenticated(username=None):
    if current_user.is_authenticated:
        return redirect(url_for('student_view.student_dashboard', username=username or current_user.username))


@studentview.route('/student_dashboard', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
@role_required('student')
def student_dashboard():
    # check if user is logged in
    user_id = current_user.get_id()
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


@studentview.route('/student_register', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
@role_required('student')
def student_register():
    user_id = current_user.get_id()
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

    newline = '\n'
    formatted_number = '+' + user.student_contact_no
    # informs the user that they are in the queue. sends the zoom link
    if user_id and request.method == 'POST':
        message = f'Hi {user.student_name}, you are now in the queue. Your adviser is {adviser_in_charge}.{newline}{newline}Please wait for your turn and do not close the page. You will receive your SMS once it is you are ready to be advised.{newline}{newline}Thank you!'
        send_sms_vonage(formatted_number, message)
        print(message)
        return redirect(url_for('studentview.waiting_page'))

    # if system detects the that user is ready to be advised
    if queue_order == 1 and not user.sms_sent:
        message = f'Dear {user.student_name},{newline}please join the zoom link: {zoom_link}{newline}Your adviser is waiting for you.'
        send_sms_vonage(formatted_number, message)
        print(message)
        user.sms_sent = True
        db.session.commit()

    return jsonify(queue_count=queue_count, queue_order=queue_order, queue_status=queue_status)


@studentview.route('/waiting_page', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
@role_required('student')
def waiting_page():
    user_id = current_user.get_id()
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


@studentview.route('/waiting-page')  # STUDENT VIEW
@login_required
@role_required('student')
def dummy_zoom():
    user_id = current_user.get_id()
    user = Student.query.get(user_id)
    queue_count = Student.query.filter_by(queue_ID=user.queue_ID).count()
    zoom_link = Admin.query.filter_by(admin_id=user.queue_ID).first().zoom_link
    queue_order = user.queue_order

    adviser_in_charge = Admin.query.filter_by(admin_id=user.queue_ID).first().admin_name
    return render_template('student/waiting-page.html',
                           adviser_in_charge=adviser_in_charge,
                           queue_count=queue_count,
                           zoom_link=zoom_link,
                           queue_order=queue_order, user=user)


@studentview.route('/get_queue_status')  # STUDENT VIEW 1 usage in zoom.html and 1 usage in waiting-page.html (AJAX)
@login_required
@role_required('student')
def get_queue_status():
    user_id = current_user.get_id()
    user = Student.query.get(user_id)
    queue_status = user.queue_status

    return jsonify(queue_status=queue_status)


@studentview.route('/feedback', methods=['GET', 'POST'])  # STUDENT VIEW 1 form usage in feedback.html
@login_required
@role_required('student')
def feedback():
    if request.method == 'POST':
        now = datetime.now()
        user_id = current_user.get_id()
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
        user.sms_sent = False
        db.session.add(student_feedback)
        db.session.commit()
        return redirect(url_for('studentview.exit_confirmation'))

    #     if user wants to log out
    return render_template('student/feedback.html')


@studentview.route('/faq', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
@role_required('student')
def faq():
    return render_template('student/faq-page.html')


@studentview.route('/exit_confirmation', methods=['GET', 'POST'])  # STUDENT VIEW
@login_required
@role_required('student')
def exit_confirmation():
    if request.method == 'POST':
        if 'Yes' in request.form:
            return redirect(url_for('studentview.student_dashboard'))
        else:
            return redirect(url_for('defaultview.logout'))

    return render_template('student/exit-confirmation.html')
