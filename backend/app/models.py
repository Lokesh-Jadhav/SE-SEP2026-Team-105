from datetime import datetime, timezone
from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, mentor, admin
    profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False, cascade="all, delete")
    mentor_profile = db.relationship("MentorProfile", backref="user", uselist=False, cascade="all, delete")


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(150), nullable=False)
    university = db.Column(db.String(200))
    goal = db.Column(db.String(50), nullable=False)  # job, masters, both
    desired_job_title = db.Column(db.String(200))
    target_country = db.Column(db.String(100))
    target_degree = db.Column(db.String(200))
    field_of_interest = db.Column(db.String(200))
    questions = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected


class MentorProfile(db.Model):
    __tablename__ = "mentor_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(150), nullable=False)
    current_status = db.Column(db.String(50), nullable=False)  # studying_abroad, working
    university = db.Column(db.String(200))
    country = db.Column(db.String(100))
    degree = db.Column(db.String(200))
    job_title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    expertise = db.Column(db.String(500), nullable=False)
    bio = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    available = db.Column(db.Boolean, default=True)


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    status = db.Column(db.String(20), default="active")  # active, pending_end, ended
    student_end_requested = db.Column(db.Boolean, default=False)
    mentor_end_requested = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    ended_at = db.Column(db.DateTime)

    student = db.relationship("User", foreign_keys=[student_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])

    messages = db.relationship("Message", backref="match", cascade="all, delete")
    meetings = db.relationship("Meeting", backref="match", cascade="all, delete")


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)

    sender = db.relationship("User")


class Availability(db.Model):
    __tablename__ = "availability_slots"

    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

    mentor = db.relationship("User")


class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey("availability_slots.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected
    meet_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utcnow)

    availability = db.relationship("Availability")


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)

    match = db.relationship("Match")
    user = db.relationship("User")

class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utcnow)

    match = db.relationship("Match", backref="goals")
    created_by = db.relationship("User")