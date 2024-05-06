#!/usr/bin/env python3

# Standard library imports
from random import choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app, db
from models import User, Course
from config import bcrypt

if __name__ == '__main__':
    fake = Faker()
    with app.app_context():

        print('Deleting ...')
        User.query.delete()
        Course.query.delete()
        
        print("Starting seed...")
        # Seed users
        print("Seeding users...")
        roles = ['Admin', 'Student', 'Instructor']
        for _ in range(10):  # Create 10 users
            password = fake.password()
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            role = rc(roles)
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                _password=hashed_password,
                role=role
            )
            db.session.add(user)

        # Seed courses
        print("Seeding courses...")
        instructors = User.query.filter_by(role='Instructor').all()  # Get instructors
        for _ in range(5):  # Create 5 courses
            course = Course(
                title=fake.text(max_nb_chars=50),
                description=fake.text(max_nb_chars=200),
                instructor_id=rc(instructors).id,  # Randomly select an instructor
                enrollment_limit=fake.random_int(min=10, max=50)
            )
            db.session.add(course)

        # Commit changes to the database
        db.session.commit()

        print("Seed completed.")
