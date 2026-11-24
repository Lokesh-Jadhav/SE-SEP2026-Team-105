# api/auth/login endpoint tests

# 1) Test /login Success
def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "password123"
    })

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data
    assert data["user"]["email"] == "student@test.com"
    assert data["user"]["role"] == "student"

# 2) Test /login with incorrect password
def test_login_wrong_password(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid email or password"
    }


# 3) Test /login with an unregistered email.
def test_login_unregistered_email(client):
    response = client.post("/api/auth/login", json={
        "email": "nobody@test.com",
        "password": "password123"
    })

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid email or password"
    }
# 4) Test /login without an email
# send a password but omit the email entirely.
def test_login_missing_email(client):
    response = client.post("/api/auth/login", json={
        "password": "password123"
    })

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid email or password"
    }


# 5) Test /login without a password
# send a email but omit the password entirely.
def test_login_missing_password(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "student@test.com"
    })

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid email or password"
    }


# 6) additional test: Email normalisation
# API uses .strip().lower() on the email. Let's verify both operations work together.
def test_login_email_normalization(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "  STUDENT@Test.COM  ",
        "password": "password123"
    })

    assert response.status_code == 200

    data = response.get_json()
    assert data["user"]["email"] == "student@test.com"


# 7) additional test: Password is case-sensitive
# stored test user password is password123. Let's try Password123.
def test_login_wrong_password_case(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "student@test.com",
        "password": "Password123"
    })

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Invalid email or password"
    }

# -----------------------------------------------------------------------------------------------------------#

# api/auth/me endpoint test

# 1) Test /me without a token

def test_me_without_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Authentication required"
    }

# 2) Test /me with Invalid JWT token

def test_me_with_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Authentication required"
    }

# get_current_user() recognises the Bearer  prefix.
# decode_token() attempts to decode the token.
# Decoding fails.The exception is caught.
# get_current_user() returns None.
# login_required() returns 401.

# 3) Test /me with Malformed Bearer header
# test a header that doesn't even follow the expected format
def test_me_with_malformed_auth_header(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Basic somecredentials"}
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Authentication required"
    }

# 4) Test /me with Valid JWT token
# A legitimate user presents a valid token.
# The endpoint should recognise them and return their details.
def test_me_with_valid_token(client, auth_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["user"]["email"] == "student@test.com"
    assert data["user"]["role"] == "student"

# 5) Test /me with an expired JWT token.
# This is different from an invalid token. An expired token can be perfectly well-formed, correctly signed and contain the correct user ID. Its expiry timestamp is simply in the past.

# The decode_token() function uses PyJWT, which checks the exp claim and raises an expiration exception when the token has expired. Your existing exception handler catches it.

def test_me_with_expired_token(client, expired_auth_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_auth_token}"}
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Authentication required"
    }

# Pytest supplies expired_auth_token. (Using fixture written in Conftest.py)
# The test sends it with the Bearer prefix.
# get_current_user() recognises the prefix.
# decode_token() attempts to decode and verify the JWT.
# PyJWT checks the exp claim and detects that it is in the past.
# An expiration exception is raised.
# Our existing except Exception catches it.
# get_current_user() returns None.
# login_required() returns HTTP 401.


# -----------------------------------------------------------------------------------------------------------#

# api/auth/register endpoint test

# 1) Test /register with Successful student registration

def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newstudent@test.com",
            "password": "Password123",
            "role": "student"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "token" in data
    assert data["user"]["email"] == "newstudent@test.com"
    assert data["user"]["role"] == "student"
    assert data["user"]["id"] is not None
    assert data["user"]["profile_completed"] is False

# 2) Test /register with successful mentor registration

def test_register_mentor_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newmentor@test.com",
            "password": "Password123",
            "role": "mentor"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "token" in data
    assert data["user"]["email"] == "newmentor@test.com"
    assert data["user"]["role"] == "mentor"
    assert data["user"]["id"] is not None
    assert data["user"]["profile_completed"] is False

# 3) Test /register with missing email

def test_register_missing_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "password": "Password123",
            "role": "student"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email, password, and valid role are required"
    }

# 4) Test /register with missing password

def test_register_missing_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newstudent@test.com",
            "role": "student"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email, password, and valid role are required"
    }

# 5) Test /register with invalid role
# all three fields are present, but the role is invalid. Send "admin" instead of "student" or "mentor".
def test_register_invalid_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "password": "Password123",
            "role": "admin"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Email, password, and valid role are required"
    }


# 6) Test /register with short password

def test_register_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "shortpass@test.com",
            "password": "1234567",
            "role": "student"
        }
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must be at least 8 characters"
    }


# 7) Test /register with duplicate email

def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "student@test.com",
            "password": "Password123",
            "role": "student"
        }
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "An account with this email already exists"
    }

# 8) Test /register email normalization

def test_register_email_normalization(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "  NEWSTUDENT@Test.COM  ",
            "password": "Password123",
            "role": "student"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["email"] == "newstudent@test.com"