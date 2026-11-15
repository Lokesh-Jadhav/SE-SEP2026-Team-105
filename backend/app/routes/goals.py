from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Match, Goal
from app.utils import login_required

goals_bp = Blueprint("goals", __name__)


def get_active_match(user):
    if user.role == "student":
        return Match.query.filter(
            Match.student_id == user.id,
            Match.status.in_(["active", "pending_end"])
        ).first()

    return Match.query.filter(
        Match.mentor_id == user.id,
        Match.status.in_(["active", "pending_end"])
    ).first()


@goals_bp.route("/", methods=["GET"])
@login_required(roles=["student", "mentor"])
def list_goals(user):
    match = get_active_match(user)

    if not match:
        return jsonify({"goals": [], "progress": {"total": 0, "completed": 0, "percentage": 0}})

    goals = Goal.query.filter_by(match_id=match.id).order_by(Goal.created_at).all()
    completed = sum(1 for goal in goals if goal.completed)

    return jsonify({
        "goals": [serialize_goal(goal) for goal in goals],
        "progress": {
            "total": len(goals),
            "completed": completed,
            "percentage": round((completed / len(goals)) * 100) if goals else 0
        }
    })


@goals_bp.route("/", methods=["POST"])
@login_required(roles=["mentor"])
def create_goal(user):
    match = get_active_match(user)

    if not match:
        return jsonify({"error": "You do not have an active mentee"}), 400

    data = request.get_json() or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Goal title is required"}), 400

    due_date = None

    if data.get("due_date"):
        try:
            due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Due date must use YYYY-MM-DD format"}), 400

    goal = Goal(
        match_id=match.id,
        created_by_id=user.id,
        title=title,
        description=data.get("description"),
        due_date=due_date
    )

    db.session.add(goal)
    db.session.commit()

    return jsonify({"message": "Goal created", "goal": serialize_goal(goal)}), 201


@goals_bp.route("/<int:goal_id>/toggle", methods=["POST"])
@login_required(roles=["student"])
def toggle_goal(user, goal_id):
    match = get_active_match(user)

    if not match:
        return jsonify({"error": "You do not have an active mentor"}), 400

    goal = Goal.query.filter_by(id=goal_id, match_id=match.id).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    goal.completed = not goal.completed
    goal.completed_at = datetime.now(timezone.utc) if goal.completed else None

    db.session.commit()

    return jsonify({"goal": serialize_goal(goal)})


@goals_bp.route("/<int:goal_id>", methods=["DELETE"])
@login_required(roles=["mentor"])
def delete_goal(user, goal_id):
    match = get_active_match(user)

    if not match:
        return jsonify({"error": "You do not have an active mentee"}), 400

    goal = Goal.query.filter_by(id=goal_id, match_id=match.id).first()

    if not goal:
        return jsonify({"error": "Goal not found"}), 404

    db.session.delete(goal)
    db.session.commit()

    return jsonify({"message": "Goal deleted"})


def serialize_goal(goal):
    return {
        "id": goal.id,
        "title": goal.title,
        "description": goal.description,
        "due_date": goal.due_date.isoformat() if goal.due_date else None,
        "completed": goal.completed,
        "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
        "created_at": goal.created_at.isoformat()
    }