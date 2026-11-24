# api/profiles/mentor endpoint tests

# 1) Test api/profiles/mentor Success
def test_save_mentor_profile_successfully(client, mentor_auth_token, mentor_user):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working",
            "expertise": "Machine Learning, Python and Data Science",
            "university": "Delhi University",
            "country": "India",
            "degree": "MSc Computer Science",
            "job_title": "Data Scientist",
            "company": "Example Technologies",
            "bio": "Experienced data scientist helping students prepare for careers."
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Mentor profile submitted for review"
    assert data["status"] == "pending"

    assert mentor_user.profile_completed is True

    from app.models import MentorProfile

    profile = MentorProfile.query.filter_by(user_id=mentor_user.id).first()

    assert profile is not None
    assert profile.full_name == "Test Mentor"
    assert profile.current_status == "working"
    assert profile.expertise == "Machine Learning, Python and Data Science"
    assert profile.university == "Delhi University"
    assert profile.country == "India"
    assert profile.degree == "MSc Computer Science"
    assert profile.job_title == "Data Scientist"
    assert profile.company == "Example Technologies"
    assert profile.bio == "Experienced data scientist helping students prepare for careers."
    assert profile.status == "pending"
    assert profile.available is True


# 2) Test api/profiles/mentor no name given

def test_save_mentor_profile_missing_full_name(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "current_status": "working",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 3) Test api/profiles/mentor no current status given

def test_save_mentor_profile_missing_current_status(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 4) Test api/profiles/mentor no expertise information given

def test_save_mentor_profile_missing_expertise(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 5) Test api/profiles/mentor invalid current status given

def test_save_mentor_profile_invalid_current_status(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "retired",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid current status"


# 6) Test api/profiles/mentor empty request given

def test_save_mentor_profile_empty_request(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={},
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 7) Test api/profiles/mentor no auth token attached

def test_save_mentor_profile_without_authentication(client):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working",
            "expertise": "Python"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 8) Test api/profiles/mentor existing mentor profile user registers again

def test_update_existing_mentor_profile(client, mentor_auth_token, mentor_user):
    # First submission creates the profile.
    first_response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert first_response.status_code == 200

    from app.models import MentorProfile

    profile = MentorProfile.query.filter_by(user_id=mentor_user.id).first()

    assert profile is not None
    original_profile_id = profile.id

    # Second submission should update the existing profile.
    second_response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Updated Mentor",
            "current_status": "studying_abroad",
            "expertise": "Deep Learning and AI",
            "university": "University of Oxford",
            "country": "United Kingdom"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert second_response.status_code == 200

    updated_profile = MentorProfile.query.filter_by(user_id=mentor_user.id).first()

    assert updated_profile is not None
    assert updated_profile.id == original_profile_id
    assert updated_profile.full_name == "Updated Mentor"
    assert updated_profile.current_status == "studying_abroad"
    assert updated_profile.expertise == "Deep Learning and AI"
    assert updated_profile.university == "University of Oxford"
    assert updated_profile.country == "United Kingdom"

    # Only one profile should exist for this user.
    assert MentorProfile.query.filter_by(user_id=mentor_user.id).count() == 1


# 9) Test api/profiles/mentor whitespace only name given

def test_save_mentor_profile_whitespace_only_name(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "   ",
            "current_status": "working",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 10) Test api/profiles/mentor whitespace only expertise given

def test_save_mentor_profile_whitespace_only_expertise(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working",
            "expertise": "   "
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name, current status, and expertise are required"


# 11) Test api/profiles/mentor mentor profile created with student(invalid) jwt token

def test_save_mentor_profile_with_student_account(client, auth_token):
    response = client.post(
        "/api/profiles/mentor",
        json={
            "full_name": "Test Mentor",
            "current_status": "working",
            "expertise": "Python"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"
