from flask import Flask
from app.config import Config
from app.extensions import db, cors
from app.models import User, StudentProfile, MentorProfile, Match, Message, Availability, Meeting, Feedback

from app.routes.auth import auth_bp
from app.routes.profiles import profiles_bp
from app.routes.admin import admin_bp
from app.routes.matching import matching_bp
from app.routes.chat import chat_bp
from app.routes.scheduling import scheduling_bp
from app.routes.mentorship import mentorship_bp
from app.routes.goals import goals_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profiles_bp, url_prefix="/api/profiles")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(matching_bp, url_prefix="/api/matching")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(scheduling_bp, url_prefix="/api/scheduling")
    app.register_blueprint(mentorship_bp, url_prefix="/api/mentorship")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")

    with app.app_context():
        db.create_all()

    return app