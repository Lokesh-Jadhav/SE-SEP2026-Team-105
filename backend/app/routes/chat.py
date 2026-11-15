from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Match, Message
from app.utils import login_required

chat_bp = Blueprint("chat", __name__)


def get_match_for_user(match_id, user):
    match = Match.query.get(match_id)

    if not match:
        return None

    if user.id not in [match.student_id, match.mentor_id]:
        return None

    return match


@chat_bp.route("/<int:match_id>", methods=["GET"])
@login_required(roles=["student", "mentor"])
def get_messages(user, match_id):
    match = get_match_for_user(match_id, user)

    if not match:
        return jsonify({"error": "Chat not found"}), 404

    now = datetime.now(timezone.utc)

    # Messages sent by the other user:
    # first load = delivered
    # subsequent load while chat is open = read
    other_messages = Message.query.filter(
        Message.match_id == match_id,
        Message.sender_id != user.id
    ).all()

    for message in other_messages:
        if not message.delivered_at:
            message.delivered_at = now

        if not message.read_at:
            message.read_at = now

    db.session.commit()

    messages = Message.query.filter_by(match_id=match_id).order_by(Message.created_at).all()

    return jsonify({
        "messages": [serialize_message(message, user.id) for message in messages]
    })


@chat_bp.route("/<int:match_id>/delivered", methods=["POST"])
@login_required(roles=["student", "mentor"])
def mark_delivered(user, match_id):
    match = get_match_for_user(match_id, user)

    if not match:
        return jsonify({"error": "Chat not found"}), 404

    now = datetime.now(timezone.utc)

    Message.query.filter(
        Message.match_id == match_id,
        Message.sender_id != user.id,
        Message.delivered_at.is_(None)
    ).update({"delivered_at": now}, synchronize_session=False)

    db.session.commit()

    return jsonify({"message": "Messages marked as delivered"})


@chat_bp.route("/<int:match_id>/read", methods=["POST"])
@login_required(roles=["student", "mentor"])
def mark_read(user, match_id):
    match = get_match_for_user(match_id, user)

    if not match:
        return jsonify({"error": "Chat not found"}), 404

    now = datetime.now(timezone.utc)

    Message.query.filter(
        Message.match_id == match_id,
        Message.sender_id != user.id,
        Message.read_at.is_(None)
    ).update({"read_at": now}, synchronize_session=False)

    db.session.commit()

    return jsonify({"message": "Messages marked as read"})


@chat_bp.route("/<int:match_id>", methods=["POST"])
@login_required(roles=["student", "mentor"])
def send_message(user, match_id):
    match = get_match_for_user(match_id, user)

    if not match:
        return jsonify({"error": "Chat not found"}), 404

    body = (request.get_json() or {}).get("body", "").strip()

    if not body:
        return jsonify({"error": "Message cannot be empty"}), 400

    message = Message(
        match_id=match_id,
        sender_id=user.id,
        body=body
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({
        "message": "Message sent",
        "data": serialize_message(message, user.id)
    }), 201


def serialize_message(message, current_user_id):
    is_mine = message.sender_id == current_user_id

    if not is_mine:
        status = None
    elif message.read_at:
        status = "read"
    elif message.delivered_at:
        status = "delivered"
    else:
        status = "sent"

    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "sender_email": message.sender.email,
        "body": message.body,
        "created_at": message.created_at.isoformat(),
        "delivered_at": message.delivered_at.isoformat() if message.delivered_at else None,
        "read_at": message.read_at.isoformat() if message.read_at else None,
        "status": status
    }