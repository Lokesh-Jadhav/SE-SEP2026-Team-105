from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User, StudentProfile, MentorProfile, Match, Feedback
from app.utils import login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/metrics", methods=["GET"])
@login_required(roles=["admin"])
def metrics(user):
    return jsonify({
        "total_students": User.query.filter_by(role="student").count(),
        "total_mentors": User.query.filter_by(role="mentor").count(),
        "pending_mentors": MentorProfile.query.filter_by(status="pending").count(),
        "pending_students": StudentProfile.query.filter_by(status="pending").count(),
        "active_matches": Match.query.filter(Match.status.in_(["active", "pending_end"])).count(),
        "ended_matches": Match.query.filter_by(status="ended").count(),
        "feedback_count": Feedback.query.count()
    })


@admin_bp.route("/students", methods=["GET"])
@login_required(roles=["admin"])
def students(user):
    profiles = StudentProfile.query.all()
    return jsonify({"students": [serialize_student(p) for p in profiles]})


@admin_bp.route("/mentors", methods=["GET"])
@login_required(roles=["admin"])
def mentors(user):
    profiles = MentorProfile.query.all()
    return jsonify({"mentors": [serialize_mentor(p) for p in profiles]})


@admin_bp.route("/students/<int:profile_id>/decision", methods=["POST"])
@login_required(roles=["admin"])
def student_decision(user, profile_id):
    profile = StudentProfile.query.get_or_404(profile_id)
    decision = request.get_json().get("decision")

    if decision not in ["approved", "rejected"]:
        return jsonify({"error": "Decision must be approved or rejected"}), 400

    profile.status = decision
    db.session.commit()

    return jsonify({"message": f"Student {decision}"})


@admin_bp.route("/mentors/<int:profile_id>/decision", methods=["POST"])
@login_required(roles=["admin"])
def mentor_decision(user, profile_id):
    profile = MentorProfile.query.get_or_404(profile_id)
    decision = request.get_json().get("decision")

    if decision not in ["approved", "rejected"]:
        return jsonify({"error": "Decision must be approved or rejected"}), 400

    profile.status = decision
    db.session.commit()

    return jsonify({"message": f"Mentor {decision}"})


@admin_bp.route("/feedback", methods=["GET"])
@login_required(roles=["admin"])
def all_feedback(user):
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()

    return jsonify({"feedback": [{
        "id": f.id,
        "match_id": f.match_id,
        "user_email": f.user.email,
        "user_role": f.user.role,
        "rating": f.rating,
        "comments": f.comments,
        "created_at": f.created_at.isoformat()
    } for f in feedback]})


def serialize_student(profile):
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": profile.user.email,
        "full_name": profile.full_name,
        "university": profile.university,
        "goal": profile.goal,
        "desired_job_title": profile.desired_job_title,
        "target_country": profile.target_country,
        "target_degree": profile.target_degree,
        "field_of_interest": profile.field_of_interest,
        "questions": profile.questions,
        "status": profile.status
    }


def serialize_mentor(profile):
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": profile.user.email,
        "full_name": profile.full_name,
        "current_status": profile.current_status,
        "university": profile.university,
        "country": profile.country,
        "degree": profile.degree,
        "job_title": profile.job_title,
        "company": profile.company,
        "expertise": profile.expertise,
        "bio": profile.bio,
        "status": profile.status,
        "available": profile.available
    }