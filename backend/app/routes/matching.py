from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User, StudentProfile, MentorProfile, Match
from app.utils import login_required

matching_bp = Blueprint("matching", __name__)


def mentor_has_active_match(mentor_id):
    return Match.query.filter(
        Match.mentor_id == mentor_id,
        Match.status.in_(["active", "pending_end"])
    ).first() is not None


def score_mentor(student, mentor):
    score = 0
    reasons = []

    student_field = (student.field_of_interest or "").lower()
    student_job = (student.desired_job_title or "").lower()
    student_country = (student.target_country or "").lower()
    student_degree = (student.target_degree or "").lower()

    mentor_expertise = (mentor.expertise or "").lower()
    mentor_job = (mentor.job_title or "").lower()
    mentor_country = (mentor.country or "").lower()
    mentor_degree = (mentor.degree or "").lower()

    if student_field and student_field in mentor_expertise:
        score += 35
        reasons.append("Field expertise matches student interest")

    if student_job and student_job in mentor_job:
        score += 25
        reasons.append("Mentor works in a similar role")

    if student_country and student_country == mentor_country:
        score += 20
        reasons.append("Same target/current country")

    if student_degree and student_degree in mentor_degree:
        score += 15
        reasons.append("Similar academic background")

    if mentor.current_status == "working" and student.goal in ["job", "both"]:
        score += 5

    if mentor.current_status == "studying_abroad" and student.goal in ["masters", "both"]:
        score += 5

    return score, reasons


@matching_bp.route("/recommendations/<int:student_user_id>", methods=["GET"])
@login_required(roles=["admin"])
def recommendations(user, student_user_id):
    student = StudentProfile.query.filter_by(user_id=student_user_id).first()

    if not student or student.status != "approved":
        return jsonify({"error": "Student must be approved before matching"}), 400

    # Exclude students who already have any match:
    # active, pending_end, or ended.
    existing_match = Match.query.filter(
        Match.student_id == student_user_id
    ).first()

    if existing_match:
        return jsonify({
            "error": "Student has already been matched previously"
        }), 409

    approved_mentors = MentorProfile.query.filter_by(
        status="approved",
        available=True
    ).all()

    ranked = []

    for mentor in approved_mentors:
        if mentor_has_active_match(mentor.user_id):
            continue

        score, reasons = score_mentor(student, mentor)

        ranked.append({
            "mentor_user_id": mentor.user_id,
            "mentor": serialize_mentor(mentor),
            "score": score,
            "reasons": reasons
        })

    ranked.sort(key=lambda item: item["score"], reverse=True)

    return jsonify({
        "top_recommendations": ranked[:3],
        "other_available_mentors": ranked[3:]
    })


@matching_bp.route("/assign", methods=["POST"])
@login_required(roles=["admin"])
def assign_mentor(user):
    data = request.get_json() or {}
    student_id = data.get("student_id")
    mentor_id = data.get("mentor_id")

    student = User.query.filter_by(id=student_id, role="student").first()
    mentor = User.query.filter_by(id=mentor_id, role="mentor").first()

    if not student or not mentor:
        return jsonify({"error": "Invalid student or mentor"}), 404

    student_profile = StudentProfile.query.filter_by(user_id=student_id).first()
    mentor_profile = MentorProfile.query.filter_by(user_id=mentor_id).first()

    if not student_profile or student_profile.status != "approved":
        return jsonify({"error": "Student is not approved"}), 400

    if not mentor_profile or mentor_profile.status != "approved":
        return jsonify({"error": "Mentor is not approved"}), 400

    if not mentor_profile.available:
        return jsonify({"error": "Mentor is currently unavailable"}), 400

    if mentor_has_active_match(mentor_id):
        return jsonify({"error": "Mentor already has an active mentee"}), 409

    if Match.query.filter(
        Match.student_id == student_id,
        Match.status.in_(["active", "pending_end"])
    ).first():
        return jsonify({"error": "Student already has an active mentor"}), 409

    match = Match(student_id=student_id, mentor_id=mentor_id)
    db.session.add(match)
    db.session.commit()

    return jsonify({"message": "Mentor assigned", "match_id": match.id}), 201


@matching_bp.route("/my-match", methods=["GET"])
@login_required(roles=["student", "mentor"])
def my_match(user):
    column = Match.student_id if user.role == "student" else Match.mentor_id

    match = Match.query.filter(
        column == user.id,
        Match.status.in_(["active", "pending_end", "ended"])
    ).order_by(Match.created_at.desc()).first()

    if not match:
        return jsonify({"match": None})

    other = match.mentor if user.role == "student" else match.student

    if user.role == "student":
        other_profile = MentorProfile.query.filter_by(user_id=other.id).first()
    else:
        other_profile = StudentProfile.query.filter_by(user_id=other.id).first()

    from app.models import Feedback

    feedback_submitted = Feedback.query.filter_by(
        match_id=match.id,
        user_id=user.id
    ).first() is not None

    return jsonify({
        "match": {
            "id": match.id,
            "status": match.status,
            "student_end_requested": match.student_end_requested,
            "mentor_end_requested": match.mentor_end_requested,
            "feedback_submitted": feedback_submitted,
            "other_user": {
                "id": other.id,
                "email": other.email,
                "full_name": other_profile.full_name if other_profile else other.email
            }
        }
    })


def serialize_mentor(profile):
    return {
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "current_status": profile.current_status,
        "university": profile.university,
        "country": profile.country,
        "degree": profile.degree,
        "job_title": profile.job_title,
        "company": profile.company,
        "expertise": profile.expertise,
        "bio": profile.bio
    }