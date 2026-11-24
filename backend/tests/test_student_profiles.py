# api/profiles/student endpoint tests

# 1) Test api/profiles/student Success
def test_save_student_profile_successfully(client, auth_token, test_user):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student",
            "goal": "job",
            "university": "IIT Madras",
            "desired_job_title": "Data Scientist",
            "target_country": "India",
            "field_of_interest": "Machine Learning",
            "questions": "How should I prepare for data science interviews?"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Student profile saved"
    assert data["status"] == "pending"

    assert test_user.profile_completed is True

    from app.models import StudentProfile

    profile = StudentProfile.query.filter_by(user_id=test_user.id).first()

    assert profile is not None
    assert profile.full_name == "Test Student"
    assert profile.goal == "job"
    assert profile.university == "IIT Madras"
    assert profile.desired_job_title == "Data Scientist"
    assert profile.target_country == "India"
    assert profile.field_of_interest == "Machine Learning"
    assert profile.questions == "How should I prepare for data science interviews?"
    assert profile.status == "pending"

# 2) Test api/profiles/student no name and career goal given

def test_save_student_profile_missing_full_name(client, auth_token):
    response = client.post(
        "/api/profiles/student",
        json={
            "goal": "job"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name and career goal are required"


# 3) Test api/profiles/student no career goal given

def test_save_student_profile_missing_goal(client, auth_token):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name and career goal are required"


# 4) Test api/profiles/student invalid career goal given

def test_save_student_profile_invalid_goal(client, auth_token):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student",
            "goal": "travel"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid career goal"


# 5) Test api/profiles/student empty request given

def test_save_student_profile_empty_request(client, auth_token):
    response = client.post(
        "/api/profiles/student",
        json={},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name and career goal are required"


# 6) Test api/profiles/student no auth token attached

def test_save_student_profile_without_authentication(client):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student",
            "goal": "job"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


# 7) Test api/profiles/student existing student profile user registers again

def test_update_existing_student_profile(client, auth_token, test_user):
    # First submission creates the profile.
    first_response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student",
            "goal": "job",
            "university": "IIT Madras"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert first_response.status_code == 200

    from app.models import StudentProfile

    profile = StudentProfile.query.filter_by(user_id=test_user.id).first()

    assert profile is not None
    original_profile_id = profile.id

    # Second submission should update the existing profile.
    second_response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Updated Student",
            "goal": "masters",
            "university": "Delhi University",
            "target_country": "Germany"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert second_response.status_code == 200

    updated_profile = StudentProfile.query.filter_by(user_id=test_user.id).first()

    assert updated_profile is not None
    assert updated_profile.id == original_profile_id
    assert updated_profile.full_name == "Updated Student"
    assert updated_profile.goal == "masters"
    assert updated_profile.university == "Delhi University"
    assert updated_profile.target_country == "Germany"

    # Only one profile should exist for this user.
    assert StudentProfile.query.filter_by(user_id=test_user.id).count() == 1


# 8) Test api/profiles/student whitespace only name given

def test_save_student_profile_whitespace_only_name(client, auth_token):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "   ",
            "goal": "job"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Full name and career goal are required"


# 9) Test api/profiles/student student profile created with mentor(invalid) jwt token

def test_save_student_profile_with_mentor_account(client, mentor_auth_token):
    response = client.post(
        "/api/profiles/student",
        json={
            "full_name": "Test Student",
            "goal": "job"
        },
        headers={"Authorization": f"Bearer {mentor_auth_token}"}
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"

