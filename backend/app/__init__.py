from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from pathlib import Path
from app.config import Config
from app.extensions import db, cors
from app.models import User, StudentProfile, MentorProfile, Match, Message, Availability, Meeting, Feedback

from app.routes.auth import auth_bp
from app.routes.profiles import profiles_bp
from app.routes.admin import admin_bp
from app.routes.matching import matching_bp
from app.routes.chat import chat_bp
# from app.routes.scheduling import scheduling_bp
# from app.routes.mentorship import mentorship_bp
from app.routes.goals import goals_bp



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #health check endpoint for smoke test
    @app.route("/")
    def home():
        return {"status": "running"}, 200

    db.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173"
                ]
            }
        },
        supports_credentials=True
    )

        # Swagger documentation
    API_DOCS_DIR = Path(__file__).resolve().parents[1] / "api_docs"

    @app.route("/openapi.yaml")
    def openapi_spec():
        return send_from_directory(
            API_DOCS_DIR,
            "mentorbridge.yaml"
        )

    swaggerui_blueprint = get_swaggerui_blueprint(
        "/docs",
        "/openapi.yaml",
        config={
            "app_name": "MentorBridge API"
        }
    )

    app.register_blueprint(swaggerui_blueprint,url_prefix="/docs")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profiles_bp, url_prefix="/api/profiles")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(matching_bp, url_prefix="/api/matching")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    # app.register_blueprint(scheduling_bp, url_prefix="/api/scheduling")
    # app.register_blueprint(mentorship_bp, url_prefix="/api/mentorship")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")

    with app.app_context():
        db.create_all()

    return app