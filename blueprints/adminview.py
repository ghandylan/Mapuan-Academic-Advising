from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import asc

from models import db, Admin, Student, Feedback
from rbac import role_required

adminview = Blueprint('adminview', __name__)


@adminview.route('/admin_dashboard', methods=['GET', 'POST'])  # ADMIN VIEW
@login_required
@role_required('admin')
def admin_dashboard():
    students = db.session.query(Student).filter(Student.queue_ID == current_user.admin_id).order_by(
        asc(Student.queue_order)).all()
    action = request.form.get('action', False)
    student_number = request.form.get('student_number', False)
    student = Student.query.filter_by(student_number=student_number).first()
    if current_user.is_authenticated:
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return the updated data in JSON format
            return jsonify({'html': render_template('admin/livelist.html',
                                                    username=current_user.admin_name,
                                                    students=students)})

        if action == 'check':
            student.queue_status = 'Fulfilled'
            if student.queue_order == 1:
                db.session.commit()
                # update queue order of all students in queue
                students = Student.query.filter(Student.queue_ID == current_user.admin_id).all()
                for student in students:
                    student.queue_order = student.queue_order - 1
                db.session.commit()
            db.session.commit()
            print(student_number)

    return render_template('admin/livelist.html',
                           username=current_user.admin_name,
                           students=students)


@adminview.route('/feedback_dashboard', methods=['GET', 'POST'])  # ADMIN VIEW
@login_required
@role_required('admin')
def feedback_dashboard():
    excellent = db.session.query(Feedback).filter(Feedback.rating == "excellent").count()
    good = db.session.query(Feedback).filter(Feedback.rating == "good").count()
    fair = db.session.query(Feedback).filter(Feedback.rating == "ok").count()
    poor = db.session.query(Feedback).filter(Feedback.rating == "poor").count()
    terrible = db.session.query(Feedback).filter(Feedback.rating == "terrible").count()

    feedback_entries = Feedback.query.all()
    feedback_entries.reverse()

    feedbacks = Feedback.query.filter_by(admin_id=current_user.admin_id).all()
    return render_template('admin/feedback-dashboard.html',
                           username=current_user.admin_name,
                           feedbacks=feedbacks,
                           excellent=excellent,
                           good=good,
                           fair=fair,
                           poor=poor,
                           terrible=terrible,
                           feedback_entries=feedback_entries)


@adminview.route('/update_zoom_link', methods=['POST'])  # ADMIN VIEW
@login_required
@role_required('admin')
def update_zoom_link():
    zoom_link = request.form['zoomLink']
    user_id = current_user.get_id()
    user = Admin.query.get(user_id)
    user.zoom_link = zoom_link
    db.session.commit()
    return redirect(url_for('adminview.edit_zoom'))


@adminview.route('/edit_zoom')  # ADMIN VIEW
@login_required
@role_required('admin')
def edit_zoom():
    admin_name = current_user.admin_name
    zoom_link = current_user.zoom_link
    status = current_user.status

    admins = Admin.query.all()

    return render_template('admin/editzoom.html',
                           username=admin_name,
                           zoom_link=zoom_link,
                           status=status,
                           admins=admins)


@adminview.route('/logout_warning', methods=['GET', 'POST'])  # ADMIN VIEW
@login_required
@role_required('admin')
def logout_warning():
    if request.method == 'POST':
        if request.form['warning'] == 'return':
            return redirect(url_for('adminview.admin_dashboard'))

    return render_template('admin/logout-warning.html')
