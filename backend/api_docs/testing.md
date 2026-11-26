# Backend API Testing Documentation

## 1. Overview

The backend API is tested using **pytest** and Flask's test client.

The test suite covers:

- Authentication APIs
- Admin APIs
- Student profile APIs
- Mentor profile APIs
- Application smoke testing

The tests verify successful requests, authentication and authorization, input validation, error handling, and expected API behaviour.

## 2. Testing Environment

| Component | Technology |
|---|---|
| Framework | pytest |
| Backend | Flask |
| Database | SQLite (temporary test database) |
| Authentication | JWT |
| HTTP testing | Flask test client |

The test fixtures are defined in `tests/conftest.py`.

Each test uses an isolated temporary SQLite database to avoid interference between test cases.

## 3. Running Tests

Run all backend tests from the `backend` directory:

```bash
python -m pytest -v
```

Run an individual test file:

```bash
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_admin_metrics.py -v
python -m pytest tests/test_admin_profiles.py -v
python -m pytest tests/test_admin_feedback.py -v
python -m pytest tests/test_student_profiles.py -v
python -m pytest tests/test_mentor_profiles.py -v
```

## 4. Test File Structure

| Test file | Coverage |
|---|---|
| `tests/test_auth.py` | Authentication and registration APIs |
| `tests/test_admin_metrics.py` | Admin dashboard metrics |
| `tests/test_admin_profiles.py` | Admin student and mentor profile management |
| `tests/test_admin_feedback.py` | Admin feedback retrieval |
| `tests/test_student_profiles.py` | Student profile APIs |
| `tests/test_mentor_profiles.py` | Mentor profile APIs |
| `tests/test_smoke.py` | Application smoke test |
| `tests/conftest.py` | Shared fixtures and test configuration |

## 5. API Test Coverage

### 5.1 Authentication APIs

Test file: `tests/test_auth.py`

The authentication test suite covers:

- Successful login
- Login with incorrect password
- Login with an unregistered email
- Missing email and password
- Email normalization
- Password case sensitivity
- Accessing the current user with a valid token
- Missing, invalid, malformed, and expired JWTs
- Successful student and mentor registration
- Missing registration fields
- Invalid user roles
- Password length validation
- Duplicate email registration

**Test count:** 20

### 5.2 Admin APIs

Admin tests cover six endpoints.

Test files:

- `tests/test_admin_metrics.py`
- `tests/test_admin_profiles.py`
- `tests/test_admin_feedback.py`

| Endpoint | Tested behaviour |
|---|---|
| `GET /api/admin/metrics` | Dashboard metrics and empty database |
| `GET /api/admin/students` | Student profile retrieval |
| `GET /api/admin/mentors` | Mentor profile retrieval |
| `POST /api/admin/students/<profile_id>/decision` | Student approval and rejection |
| `POST /api/admin/mentors/<profile_id>/decision` | Mentor approval and rejection |
| `GET /api/admin/feedback` | Feedback retrieval and ordering |

Additional test cases verify:

- Successful admin authentication
- Missing authentication
- Invalid JWT
- Requests made using a non-admin token
- Invalid or missing decision values
- Nonexistent profile IDs
- Empty database responses

**Test count:** 35

### 5.3 Student Profile APIs

Test file: `tests/test_student_profiles.py`

Coverage includes:

- Successful profile creation
- Missing full name
- Missing or invalid goal
- Empty request body
- Missing authentication
- Updating an existing profile
- Whitespace-only name validation
- Requests made using a mentor account

**Test count:** 9

### 5.4 Mentor Profile APIs

Test file: `tests/test_mentor_profiles.py`

Coverage includes:

- Successful profile creation
- Missing full name
- Missing current status
- Missing expertise
- Invalid current status
- Empty request body
- Missing authentication
- Updating an existing profile
- Whitespace-only name validation
- Whitespace-only expertise validation
- Requests made using a student account

**Test count:** 11

### 5.5 Application Smoke Test

Test file: `tests/test_smoke.py`

Verifies that the application home page responds successfully.

**Test count:** 1

## 6. Test Execution and Evidence

The complete backend test suite can be executed using:

```bash
python -m pytest -v
```

The verbose output provides:

- Individual test names
- Execution status for each test
- Failure details and assertion information
- A final summary of collected, passed, and failed tests
