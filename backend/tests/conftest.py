import pytest
import datetime
import jwt
from app import create_app
from app.extensions import db
from app.config import Config
from app.utils import create_token
from werkzeug.security import generate_password_hash
from app.models import User

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "pytest-test-secret-key-2026-long-enough"   #change to env variable hex key in prod.
    JWT_EXPIRY_HOURS = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def app(tmp_path):
    TestingConfig.SQLALCHEMY_DATABASE_URI = (f"sqlite:///{tmp_path / 'test.db'}")

    app = create_app(TestingConfig)
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# Admin API test fixtures
@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(
            email="admin@test.com",
            password_hash=generate_password_hash("password123"),
            role="admin"
        )
        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()


# Create a JWT for the admin
@pytest.fixture
def admin_auth_token(app, admin_user):
    with app.app_context():
        return create_token(admin_user)


# Login and student/mentor profile test fixtures
@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email="student@test.com",
            password_hash=generate_password_hash("password123"),
            role="student"
        )

        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()

#create JWT for student
@pytest.fixture
def auth_token(app, test_user):
    with app.app_context():
        return create_token(test_user)

# Create an expired JWT
@pytest.fixture
def expired_auth_token(app, test_user):
    payload = {
        "user_id": test_user.id,
        "role": test_user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
    }

    return jwt.encode(
        payload,
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

# Create a mentor user for mentor profile tests
@pytest.fixture
def mentor_user(app):
    with app.app_context():
        user = User(
            email="mentor@test.com",
            password_hash=generate_password_hash("password123"),
            role="mentor"
        )
        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()


# Create a JWT for the mentor
@pytest.fixture
def mentor_auth_token(app, mentor_user):
    with app.app_context():
        return create_token(mentor_user)
