from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import mariadb

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATAdb.Model_URI'] = 'mysql+:mariadb://root:@localhost:3306/academic-advising'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Student(db.Model):
    student_number = db.Column(db.Integer, primary_key=True)
    student_email = db.Column(db.String(50), nullable=False)
    student_password = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(50), nullable=False)
    student_contact = db.Column(db.String(50), nullable=False)
    student_program = db.Column(db.String(50), nullable=False)
    student_year = db.Column(db.String(50), nullable=False)
    student_concern = db.Column(db.String(50), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'), nullable=False)
    is_student = db.Column(db.Boolean, nullable=False)


class Admin(db.Model):
    __tablename__ = 'admin'
    admin_number = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(50), nullable=False)
    admin_password = db.Column(db.String(50), nullable=False)
    admin_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)


class Queue(db.Model):
    __tablename__ = 'queue'
    queue_id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.Integer, db.ForeignKey('student.student_number'),
                               nullable=False)
    admin_number = db.Column(db.Integer, db.ForeignKey('admin.admin_number'), nullable=False)
    queue_status = db.Column(db.String(50), nullable=False)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.Integer, db.ForeignKey('student.student_number'),
                               nullable=False)
    admin_number = db.Column(db.Integer, db.ForeignKey('admin.admin_number'), nullable=False)
    feedback = db.Column(db.String(50), nullable=False)


class Class(db.Model):
    __tablename__ = 'class'
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    class_code = db.Column(db.String(50), nullable=False)
    teacher_name = db.Column(db.String(50), nullable=False)
    admin_number = db.Column(db.Integer, db.ForeignKey('admin.admin_number'), nullable=False)