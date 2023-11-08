from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

db = SQLAlchemy()


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
    sms_sent = db.Column(Boolean, nullable=False, default=False)
    role = db.Column(String(255), nullable=False, default="student")

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
    role = db.Column(String(255), nullable=False, default="admin")

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
