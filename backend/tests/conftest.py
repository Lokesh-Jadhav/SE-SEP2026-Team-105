import pytest
from app import create_app
from app.extensions import db
from app.config import Config

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "pytest-test-secret"   #change to env variable hex key in prod.
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