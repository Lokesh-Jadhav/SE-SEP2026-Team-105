
# /api/admin/students tests

# 1) Test /api/admin/students Success

def test_admin_students_successfully(client, admin_auth_token, test_user):
    from app.extensions import db
    from app.models import StudentProfile

    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        university="IIT Madras",
        goal="job",
        desired_job_title="Data Scientist",
        target_country="India",
        target_degree=None,
        field_of_interest="Data Science",
        questions="How do I prepare for interviews?",
        status="pending"
    )

    db.session.add(profile)
    db.session.commit()

    response = client.get(
        "/api/admin/students",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["students"]) == 1

    student = data["students"][0]

    assert student["id"] == profile.id
    assert student["user_id"] == test_user.id
    assert student["email"] == test_user.email
    assert student["full_name"] == "Test Student"
    assert student["university"] == "IIT Madras"
    assert student["goal"] == "job"
    assert student["desired_job_title"] == "Data Scientist"
    assert student["target_country"] == "India"
    assert student["target_degree"] is None
    assert student["field_of_interest"] == "Data Science"
    assert student["questions"] == "How do I prepare for interviews?"
    assert student["status"] == "pending"


# 2) Test /api/admin/students empty database

def test_admin_students_with_empty_database(client, admin_auth_token):
    response = client.get(
        "/api/admin/students",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"students": []}


# 3) Test /api/admin/students without authentication

def test_admin_students_without_authentication(client):
    response = client.get("/api/admin/students")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 4) Test /api/admin/students with invalid token

def test_admin_students_with_invalid_token(client):
    response = client.get(
        "/api/admin/students",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 5) Test /api/admin/students with student authentication

def test_admin_students_with_student_token(client, auth_token):
    response = client.get(
        "/api/admin/students",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"



# /api/admin/mentors tests

# 1) Test /api/admin/mentors Success

def test_admin_mentors_successfully(client, admin_auth_token):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, MentorProfile

    mentor = User(
        email="mentor_admin@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )

    db.session.add(mentor)
    db.session.commit()

    profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        university="IIT Delhi",
        country="USA",
        degree="MS Computer Science",
        job_title="Software Engineer",
        company="Google",
        expertise="Python and Machine Learning",
        bio="Experienced software engineer and mentor.",
        status="pending",
        available=True
    )

    db.session.add(profile)
    db.session.commit()

    response = client.get(
        "/api/admin/mentors",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["mentors"]) == 1

    mentor_data = data["mentors"][0]

    assert mentor_data["id"] == profile.id
    assert mentor_data["user_id"] == mentor.id
    assert mentor_data["email"] == mentor.email
    assert mentor_data["full_name"] == "Test Mentor"
    assert mentor_data["current_status"] == "working"
    assert mentor_data["university"] == "IIT Delhi"
    assert mentor_data["country"] == "USA"
    assert mentor_data["degree"] == "MS Computer Science"
    assert mentor_data["job_title"] == "Software Engineer"
    assert mentor_data["company"] == "Google"
    assert mentor_data["expertise"] == "Python and Machine Learning"
    assert mentor_data["bio"] == "Experienced software engineer and mentor."
    assert mentor_data["status"] == "pending"
    assert mentor_data["available"] is True


# 2) Test /api/admin/mentors empty database

def test_admin_mentors_with_empty_database(client, admin_auth_token):
    response = client.get(
        "/api/admin/mentors",
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"mentors": []}


# 3) Test /api/admin/mentors without authentication

def test_admin_mentors_without_authentication(client):
    response = client.get("/api/admin/mentors")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 4) Test /api/admin/mentors with invalid token

def test_admin_mentors_with_invalid_token(client):
    response = client.get(
        "/api/admin/mentors",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 5) Test /api/admin/mentors with student authentication

def test_admin_mentors_with_student_token(client, auth_token):
    response = client.get(
        "/api/admin/mentors",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"



# /api/admin/students/<profile_id>/decision tests

# 1) Test /api/admin/students/<profile_id>/decision approve student

def test_admin_student_decision_approve(client, admin_auth_token, test_user):
    from app.extensions import db
    from app.models import StudentProfile

    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        goal="job",
        status="pending"
    )

    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/students/{profile.id}/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Student approved"

    updated_profile = db.session.get(StudentProfile, profile.id)
    assert updated_profile.status == "approved"


# 2) Test /api/admin/students/<profile_id>/decision reject student

def test_admin_student_decision_reject(client, admin_auth_token, test_user):
    from app.extensions import db
    from app.models import StudentProfile

    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        goal="job",
        status="pending"
    )

    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/students/{profile.id}/decision",
        json={"decision": "rejected"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Student rejected"

    updated_profile = db.session.get(StudentProfile, profile.id)
    assert updated_profile.status == "rejected"


# 3) Test /api/admin/students/<profile_id>/decision invalid decision

def test_admin_student_decision_invalid_value(client, admin_auth_token, test_user):
    from app.extensions import db
    from app.models import StudentProfile

    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        goal="job",
        status="pending"
    )

    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/students/{profile.id}/decision",
        json={"decision": "waiting"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Decision must be approved or rejected"

    unchanged_profile = db.session.get(StudentProfile, profile.id)
    assert unchanged_profile.status == "pending"


# 4) Test /api/admin/students/<profile_id>/decision missing decision

def test_admin_student_decision_missing_value(client, admin_auth_token, test_user):
    from app.extensions import db
    from app.models import StudentProfile

    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        goal="job",
        status="pending"
    )

    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/students/{profile.id}/decision",
        json={},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Decision must be approved or rejected"

    unchanged_profile = db.session.get(StudentProfile, profile.id)
    assert unchanged_profile.status == "pending"


# 5) Test /api/admin/students/<profile_id>/decision nonexistent profile

def test_admin_student_decision_nonexistent_profile(client, admin_auth_token):
    response = client.post(
        "/api/admin/students/9999/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 404


# 6) Test /api/admin/students/<profile_id>/decision without authentication

def test_admin_student_decision_without_authentication(client):
    response = client.post(
        "/api/admin/students/1/decision",
        json={"decision": "approved"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 7) Test /api/admin/students/<profile_id>/decision with student authentication

def test_admin_student_decision_with_student_token(client, auth_token):
    response = client.post(
        "/api/admin/students/1/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"



# /api/admin/mentors/<profile_id>/decision tests

# 1) Test /api/admin/mentors/<profile_id>/decision approve mentor

def test_admin_mentor_decision_approve(client, admin_auth_token):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, MentorProfile

    mentor = User(
        email="mentor_approve@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )
    db.session.add(mentor)
    db.session.commit()

    profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        expertise="Python",
        status="pending"
    )
    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/mentors/{profile.id}/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Mentor approved"

    updated_profile = db.session.get(MentorProfile, profile.id)
    assert updated_profile.status == "approved"


# 2) Test /api/admin/mentors/<profile_id>/decision reject mentor

def test_admin_mentor_decision_reject(client, admin_auth_token):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, MentorProfile

    mentor = User(
        email="mentor_reject@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )
    db.session.add(mentor)
    db.session.commit()

    profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        expertise="Python",
        status="pending"
    )
    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/mentors/{profile.id}/decision",
        json={"decision": "rejected"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Mentor rejected"

    updated_profile = db.session.get(MentorProfile, profile.id)
    assert updated_profile.status == "rejected"


# 3) Test /api/admin/mentors/<profile_id>/decision invalid decision

def test_admin_mentor_decision_invalid_value(client, admin_auth_token):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, MentorProfile

    mentor = User(
        email="mentor_invalid@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )
    db.session.add(mentor)
    db.session.commit()

    profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        expertise="Python",
        status="pending"
    )
    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/mentors/{profile.id}/decision",
        json={"decision": "waiting"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Decision must be approved or rejected"

    unchanged_profile = db.session.get(MentorProfile, profile.id)
    assert unchanged_profile.status == "pending"


# 4) Test /api/admin/mentors/<profile_id>/decision missing decision

def test_admin_mentor_decision_missing_value(client, admin_auth_token):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User, MentorProfile

    mentor = User(
        email="mentor_missing@test.com",
        password_hash=generate_password_hash("password123"),
        role="mentor"
    )
    db.session.add(mentor)
    db.session.commit()

    profile = MentorProfile(
        user_id=mentor.id,
        full_name="Test Mentor",
        current_status="working",
        expertise="Python",
        status="pending"
    )
    db.session.add(profile)
    db.session.commit()

    response = client.post(
        f"/api/admin/mentors/{profile.id}/decision",
        json={},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Decision must be approved or rejected"

    unchanged_profile = db.session.get(MentorProfile, profile.id)
    assert unchanged_profile.status == "pending"


# 5) Test /api/admin/mentors/<profile_id>/decision nonexistent profile

def test_admin_mentor_decision_nonexistent_profile(client, admin_auth_token):
    response = client.post(
        "/api/admin/mentors/9999/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {admin_auth_token}"}
    )

    assert response.status_code == 404


# 6) Test /api/admin/mentors/<profile_id>/decision without authentication

def test_admin_mentor_decision_without_authentication(client):
    response = client.post(
        "/api/admin/mentors/1/decision",
        json={"decision": "approved"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 7) Test /api/admin/mentors/<profile_id>/decision with student authentication

def test_admin_mentor_decision_with_student_token(client, auth_token):
    response = client.post(
        "/api/admin/mentors/1/decision",
        json={"decision": "approved"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"
