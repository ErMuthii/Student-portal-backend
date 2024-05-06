from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship,validates
from datetime import datetime
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'
    #admin class
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    def __init__(self, username, email, _password, role='student'):
        self.username = username
        self.email = email
        self._password = _password
        self.role = role

    @validates('password')
    def validate_password(self,key,password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, plaintext_password):
        return bcrypt.check_password_hash(self._password, plaintext_password)

class Course(db.Model, SerializerMixin):
    __tablename__ = 'course'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # categories, 
    #flask uploads
    description = db.Column(db.Text, nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    enrollment_limit = db.Column(db.Integer, nullable=False)

    instructor = db.relationship('User', backref=db.backref('courses_taught', lazy='dynamic'))
    enrolled_students = db.relationship('User', secondary='enrollments', backref=db.backref('enrolled_courses', lazy='dynamic'))

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)

class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
