# /api/admin/metrics tests

# 1) Test /api/admin/metrics Success

def test_admin_metrics_successfully(client, admin_auth_token, test_user):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import (
        User,
        StudentProfile,
        MentorProfile,
        Match,
        Feedback
    )

    # Create a mentor user.
    mentor = User(
        email="mentor_metrics@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )

    db.session.add(mentor)
    db.session.commit()

    # Create student and mentor profiles.
    student_profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        goal="job",
        status="pending"
    )

    mentor_profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        expertise="Python",
        status="pending"
    )

    db.session.add_all([student_profile, mentor_profile])
    db.session.commit()

    # Create matches with different statuses.
    active_match = Match(
        student_id=test_user.id,
        mentor_id=mentor.id,
        status="active"
    )

    pending_end_match = Match(
        student_id=test_user.id,
        mentor_id=mentor.id,
        status="pending_end"
    )

    ended_match = Match(
        student_id=test_user.id,
        mentor_id=mentor.id,
        status="ended"
    )

    db.session.add_all([
        active_match,
        pending_end_match,
        ended_match
    ])
    db.session.commit()

    # Create feedback.
    feedback = Feedback(
        match_id=active_match.id,
        user_id=test_user.id,
        rating=5,
        comments="Excellent mentoring experience."
    )

    db.session.add(feedback)
    db.session.commit()

    response = client.get(
        "/api/admin/metrics",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_students"] == 1
    assert data["total_mentors"] == 1
    assert data["pending_students"] == 1
    assert data["pending_mentors"] == 1
    assert data["active_matches"] == 2
    assert data["ended_matches"] == 1
    assert data["feedback_count"] == 1


# 2) Test /api/admin/metrics empty database for metrics

def test_admin_metrics_with_empty_database(client, admin_auth_token):
    response = client.get(
        "/api/admin/metrics",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_students"] == 0
    assert data["total_mentors"] == 0
    assert data["pending_students"] == 0
    assert data["pending_mentors"] == 0
    assert data["active_matches"] == 0
    assert data["ended_matches"] == 0
    assert data["feedback_count"] == 0


# 3) Test /api/admin/metrics without authentication

def test_admin_metrics_without_authentication(client):
    response = client.get("/api/admin/metrics")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 4) Test /api/admin/metrics with invalid token

def test_admin_metrics_with_invalid_token(client):
    response = client.get(
        "/api/admin/metrics",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 5) Test /api/admin/metrics with student authentication

def test_admin_metrics_with_student_token(client, auth_token):
    response = client.get(
        "/api/admin/metrics",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"
