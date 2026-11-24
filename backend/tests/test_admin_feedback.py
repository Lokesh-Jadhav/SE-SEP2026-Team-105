
# /api/admin/feedback tests

# 1) Test /api/admin/feedback Success

def test_admin_feedback_successfully(client, admin_auth_token, test_user):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, Match, Feedback

    mentor = User(
        email="mentor_feedback@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )

    db.session.add(mentor)
    db.session.commit()

    match = Match(
        student_id=test_user.id,
        mentor_id=mentor.id,
        status="active"
    )

    db.session.add(match)
    db.session.commit()

    feedback = Feedback(
        match_id=match.id,
        user_id=test_user.id,
        rating=5,
        comments="Excellent mentoring experience."
    )

    db.session.add(feedback)
    db.session.commit()

    response = client.get(
        "/api/admin/feedback",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["feedback"]) == 1

    feedback_data = data["feedback"][0]

    assert feedback_data["id"] == feedback.id
    assert feedback_data["match_id"] == match.id
    assert feedback_data["user_email"] == test_user.email
    assert feedback_data["user_role"] == "student"
    assert feedback_data["rating"] == 5
    assert feedback_data["comments"] == "Excellent mentoring experience."
    assert feedback_data["created_at"] is not None


# 2) Test /api/admin/feedback empty database

def test_admin_feedback_with_empty_database(client, admin_auth_token):
    response = client.get(
        "/api/admin/feedback",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"feedback": []}


# 3) Test /api/admin/feedback newest feedback first

def test_admin_feedback_newest_first(client, admin_auth_token, test_user):
    from datetime import datetime, timezone

    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, Match, Feedback

    mentor = User(
        email="mentor_order@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )

    db.session.add(mentor)
    db.session.commit()

    match = Match(
        student_id=test_user.id,
        mentor_id=mentor.id,
        status="active"
    )

    db.session.add(match)
    db.session.commit()

    older_feedback = Feedback(
        match_id=match.id,
        user_id=test_user.id,
        rating=3,
        comments="Older feedback",
        created_at=datetime(2026, 11, 20, tzinfo=timezone.utc)
    )

    newer_feedback = Feedback(
        match_id=match.id,
        user_id=test_user.id,
        rating=5,
        comments="Newer feedback",
        created_at=datetime(2026, 11, 24, tzinfo=timezone.utc)
    )

    db.session.add_all([older_feedback, newer_feedback])
    db.session.commit()

    response = client.get(
        "/api/admin/feedback",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    feedback_list = response.get_json()["feedback"]

    assert len(feedback_list) == 2
    assert feedback_list[0]["comments"] == "Newer feedback"
    assert feedback_list[1]["comments"] == "Older feedback"


# 4) Test /api/admin/feedback without authentication

def test_admin_feedback_without_authentication(client):
    response = client.get("/api/admin/feedback")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 5) Test /api/admin/feedback with invalid token

def test_admin_feedback_with_invalid_token(client):
    response = client.get(
        "/api/admin/feedback",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 6) Test /api/admin/feedback with student authentication

def test_admin_feedback_with_student_token(client, auth_token):
    response = client.get(
        "/api/admin/feedback",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"
