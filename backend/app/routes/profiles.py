from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import StudentProfile, MentorProfile
from app.utils import login_required

profiles_bp = Blueprint("profiles", __name__)


@profiles_bp.route("/student", methods=["POST"])
@login_required(roles=["student"])
def save_student_profile(user):
    data = request.get_json() or {}

    required = ["full_name", "goal"]
    if any(not data.get(field) for field in required):
        return jsonify({"error": "Full name and career goal are required"}), 400

    if data.get("goal") not in ["job", "masters", "both"]:
        return jsonify({"error": "Invalid career goal"}), 400

    profile = StudentProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.session.add(profile)

    profile.full_name = data["full_name"]
    profile.university = data.get("university")
    profile.goal = data["goal"]
    profile.desired_job_title = data.get("desired_job_title")
    profile.target_country = data.get("target_country")
    profile.target_degree = data.get("target_degree")
    profile.field_of_interest = data.get("field_of_interest")
    profile.questions = data.get("questions")
    profile.status = "pending"

    user.profile_completed = True
    db.session.commit()

    return jsonify({"message": "Student profile saved", "status": profile.status})


@profiles_bp.route("/mentor", methods=["POST"])
@login_required(roles=["mentor"])
def save_mentor_profile(user):
    data = request.get_json() or {}

    required = ["full_name", "current_status", "expertise"]
    if any(not data.get(field) for field in required):
        return jsonify({"error": "Full name, current status, and expertise are required"}), 400

    if data.get("current_status") not in ["studying_abroad", "working"]:
        return jsonify({"error": "Invalid current status"}), 400

    profile = MentorProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        profile = MentorProfile(user_id=user.id)
        db.session.add(profile)

    profile.full_name = data["full_name"]
    profile.current_status = data["current_status"]
    profile.university = data.get("university")
    profile.country = data.get("country")
    profile.degree = data.get("degree")
    profile.job_title = data.get("job_title")
    profile.company = data.get("company")
    profile.expertise = data["expertise"]
    profile.bio = data.get("bio")
    profile.status = "pending"
    profile.available = True

    user.profile_completed = True
    db.session.commit()

    return jsonify({"message": "Mentor profile submitted for review", "status": profile.status})


@profiles_bp.route("/me", methods=["GET"])
@login_required(roles=["student", "mentor"])
def get_my_profile(user):
    if user.role == "student":
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
    else:
        profile = MentorProfile.query.filter_by(user_id=user.id).first()

    return jsonify({"profile": serialize_profile(profile) if profile else None})


def serialize_profile(profile):
    return {column.name: getattr(profile, column.name) for column in profile.__table__.columns}